from azureml.core import Run, Dataset
import argparse
from azureml.core.compute import ComputeTarget
import os


#Parse Input Arguments
parser = argparse.ArgumentParser("Retrieve AML Dataset and Launch AutoML for Images Job")
parser.add_argument("--model_name", type=str, required=True)
parser.add_argument("--dataset_name", type=str, required=True)
parser.add_argument("--compute_name", type=str, required=True)
args, _ = parser.parse_known_args()
model_name = args.model_name
dataset_name = args.dataset_name
compute_name = args.compute_name

#Get current run and AML workspace
current_run = Run.get_context()
ws = current_run.experiment.workspace
experiment_name = current_run.experiment.name

compute_target = ComputeTarget(workspace=ws, name=compute_name)

from azureml.automl.core.shared.constants import ImageTask
from azureml.train.automl import AutoMLImageConfig
from azureml.train.hyperdrive import BanditPolicy, RandomParameterSampling
from azureml.train.hyperdrive import choice, uniform

from azureml.core import Dataset
dataset = Dataset.get_by_name(ws, name=dataset_name)
formatted_datasets = [('Training_Data', dataset)]


from azureml.train.automl import AutoMLImageConfig
from azureml.train.hyperdrive import GridParameterSampling, choice
from azureml.automl.core.shared.constants import ImageTask

parameter_space = {
    "model": choice(
        {
            "model_name": choice("yolov5"),
            "learning_rate": uniform(0.0001, 0.01),
            "model_size": choice("small", "medium"),  # model-specific
            #'img_size': choice(640, 704, 768), # model-specific; might need GPU with large memory
        }
    ),
}

tuning_settings = {
    "iterations": 1,
    "max_concurrent_iterations": 5,
    "hyperparameter_sampling": RandomParameterSampling(parameter_space),
    "early_termination_policy": BanditPolicy(
        evaluation_interval=2, slack_factor=0.2, delay_evaluation=6
    ),
}

image_automl_config = AutoMLImageConfig(
    task=ImageTask.IMAGE_OBJECT_DETECTION,
    compute_target=compute_target,
    training_data=dataset,
    **tuning_settings
)

new_run = current_run.submit_child(image_automl_config)
new_run.wait_for_completion()

best_child_run = new_run.get_best_child()
metrics = best_child_run.get_metrics()
mAP = max(metrics['mean_average_precision'])

updated_tags = {'Mean Average Precision': mAP}

os.makedirs('tmp')

best_child_run.download_files(prefix='./outputs', output_directory='tmp',append_prefix=True)
best_child_run.download_files(prefix='./train_artifacts', output_directory='tmp',append_prefix=True)

current_run.upload_folder('automl_outputs', 'tmp')

model = current_run.register_model(model_name, model_path='automl_outputs', model_framework='Azure ML - AutoML for Images (Yolov5)', tags=updated_tags, datasets=formatted_datasets, sample_input_dataset = dataset)

