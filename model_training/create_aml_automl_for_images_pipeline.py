from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.runconfig import DEFAULT_GPU_IMAGE
from azureml.pipeline.core import Pipeline, PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import PipelineParameter, PipelineEndpoint
import os

#Connect to AML Workspace
subscription_id = os.getenv("SUBSCRIPTION_ID")
resource_group = os.getenv("RESOURCE_GROUP")
workspace_name = os.getenv("WORKSPACE_NAME")
workspace_region = os.getenv("WORKSPACE_REGION")


try:
    # ws = Workspace.from_config()
    ws = Workspace(subscription_id=subscription_id, 
                   resource_group=resource_group, 
                   workspace_name=workspace_name)
    print("Workspace configuration succeeded. Skip the workspace creation steps below")
except:
    print("Workspace does not exist. Creating workspace")
    ws = Workspace.create(name=workspace_name, subscription_id=subscription_id, resource_group=resource_group,
                            location=workspace_region, create_resource_group=True, exist_ok=True)

cluster_name = os.getenv("AML_COMPUTE_CLUSTER_NAME")
# compute_target = ws.compute_targets[cluster_name]
try:
    compute_target = ComputeTarget(workspace=ws, name=cluster_name)
    print("Found existing compute target.")
except ComputeTargetException:
    print("Creating a new compute target...")
    compute_config = AmlCompute.provisioning_configuration(
        vm_size=os.getenv("VM_SIZE"),
        idle_seconds_before_scaledown=os.getenv("IDLE_SECONDS_BEFORE_SCALEDOWN"),
        min_nodes=int(os.getenv("AML_CLUSTER_MIN_NODES")),
        max_nodes=int(os.getenv("AML_CLUSTER_MAX_NODES")),
    )
    compute_target = ComputeTarget.create(ws, cluster_name, compute_config)
    # Can poll for a minimum number of nodes and for a specific timeout.
    # If no min_node_count is provided, it will use the scale settings for the cluster.
    compute_target.wait_for_completion(
        show_output=True, min_node_count=None, timeout_in_minutes=20
    )
    
#Get default datastore
default_ds = ws.get_default_datastore()

run_config = RunConfiguration()
run_config.environment.docker.base_image = DEFAULT_GPU_IMAGE
run_config.environment.python.conda_dependencies = CondaDependencies.create()
run_config.environment.python.conda_dependencies.add_conda_package("numpy==1.18.5")
run_config.environment.python.conda_dependencies.add_conda_package("libffi=3.3")
run_config.environment.python.conda_dependencies.set_pip_requirements([
    "azureml-core==1.37.0",
    "azureml-mlflow==1.37.0",
    "azureml-dataset-runtime==1.37.0",
    "azureml-telemetry==1.37.0",
    "azureml-responsibleai==1.37.0",
    "azureml-automl-core==1.37.0",
    "azureml-automl-runtime==1.37.0",
    "azureml-train-automl-client==1.37.0",
    "azureml-defaults==1.37.0",
    "azureml-interpret==1.37.0",
    "azureml-train-automl-runtime==1.37.0",
    "azureml-automl-dnn-vision==1.37.0",
    "azureml-dataprep>=2.24.4"
])
run_config.environment.python.conda_dependencies.set_python_version('3.7')
run_config.environment.name = "AutoMLForImagesEnv"
run_config.environment.register(ws)



model_name = PipelineParameter(name='model_name', default_value='Model_Name')
dataset_name = PipelineParameter(name='dataset_name', default_value='Dataset_Name')
compute_name = PipelineParameter(name='compute_name', default_value=os.getenv("AML_COMPUTE_CLUSTER_NAME"))

submit_job_step = PythonScriptStep(
    name='Submit AutoML Job',
    script_name=os.getenv('AUTOML_JOB_SUBMIT_PIPELINE_SCRIPT'),
    arguments=[
        '--model_name', model_name,
        '--dataset_name', dataset_name,
        '--compute_name', compute_name,
    ],
    compute_target=compute_target,
    source_directory=os.getenv('PIPELINE_STEPS_DIR'),
    allow_reuse=False,
    runconfig=run_config
)

pipeline = Pipeline(workspace=ws, steps=[submit_job_step])

build_id = os.getenv('BUILD_BUILDID', default='1')
pipeline_name = os.getenv("PIPELINE_NAME", default=os.getenv('AUTOML_PIPELINE_NAME'))

published_pipeline = pipeline.publish(name = pipeline_name,
                                        version=build_id,
                                     description = os.getenv('AUTOML_PIPELINE_DESCRIPTION'),
                                     continue_on_step_failure = False)

try:
    pipeline_endpoint = PipelineEndpoint.get(
        workspace=ws, name=os.getenv('AUTOML_PIPELINE_NAME')
    )
    print("using existing PipelineEndpoint...")
    pipeline_endpoint.add_default(published_pipeline)
except Exception as ex:
    print(ex)
    # create PipelineEndpoint if it doesn't exist
    print("PipelineEndpoint does not exist, creating one for you...")
    pipeline_endpoint = PipelineEndpoint.publish(
        workspace=ws,
        name=os.getenv('AUTOML_PIPELINE_NAME'),
        pipeline=published_pipeline,
        description=os.getenv('AUTOML_PIPELINE_DESCRIPTION')
    )
