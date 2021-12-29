
# Create Custom Object Detection Models using Azure Machine Learning & AutoML for Images

Set up a CI pipeline inside of Azure DevOps to publish an Azure Machine Learning Pipeline for training object detection models. Models trained through via this AML pipeline are automatically added to a model registry and can be deployed to the edge.

The guided walkthrough below highlights how to deploy an Azure Machine Learning pipeline via a CI pipeline in Azure DevOps, how to create a labeled dataset in Azure ML using images sourced from blob storage, and how to train a custom object detection model using Azure ML's AutoML for Images functionality.
 - [Step 1 - Create Azure DevOps Service Connection to Machine Learning Workspace](https://github.com/rutzsco/computer-vision-accelerator/tree/mlops/model_training#step-1---create-azure-devops-service-connection-to-machine-learning-workspace)
 - [Step 2 - Deploy and Run CI Pipeline for Updating Azure Machine Learning AutoML for Images Pipeline](#step-2---deploy-and-run-ci-pipeline-for-updating-azure-machine-learning-automl-for-images-pipeline)
 - [Step 3 - Register your Azure Storage Account used for Image Capture as an Azure Machine Learning Datastore](#step-3---register-your-azure-storage-account-used-for-image-capture-as-an-azure-machine-learning-datastore)
 - [Step 4 - Create a Labeled Dataset using the Azure Machine Learning Data Labeler Tools](#step-4---create-a-labeled-dataset-using-the-azure-machine-learning-data-labeler-tools)
 - [Step 5 - Train a New Object Detection Model](#step-5---train-a-new-object-detection-model)


<b>Note: </b> Prior to completing any of the steps below, deploy all required Azure infrastructure using the IaC pipeline at `path\to\dir\pipeline.yaml`.

## Step 1 - Create Azure DevOps Service Connection to Machine Learning Workspace

From your Azure DevOps project, create a new service connection to your Azure Machine Learning Workspace.

* Navigate to Project Settings, then to Service Connections, and click <i>New service connection</i>.

![Service Connections](doc_img/01.png?raw=true "Service Connections")

* Select Azure Resource Manager then click <i>Next</i>.

![Azure Resource Manager](doc_img/02.png?raw=true "Azure Resource Manager")

* Leave Service principal (automatic) selected and click <i>Next</i>.

![Service Principal Automatic](doc_img/03.png?raw=true "Service Principal Automatic")

* Under Scope level, select <i>Machine Learning Workspace</i>, then choose the appropriate subscription, resource group, and AML resource. Name your service connection `aml-workspace-connection`. Finally, under security, check <i>Grant access permission to all pipelines</i> then click <i>Save</i>.  

![AML Workspace Connection](doc_img/04.png?raw=true "AML Workspace Connection")

## Step 2 - Deploy and Run CI Pipeline for Updating Azure Machine Learning AutoML for Images Pipeline

From your Azure DevOps project, create a new CI pipeline using the yaml definition at `model_training/.pipelines/publish_aml_pipeline.yml`.

* Navigate to Pipelines and click <i>New Pipeline</i>.

![New Pipeline](doc_img/05.png?raw=true "New Pipeline")

* When prompted to connect your code, select GitHub and navigate to your forked repository.

![Connect to Forked Repo](doc_img/06.png?raw=true "Connect to Forked Repo")

* When prompted to configure your pipeline, choose the <i>Existing Azure Pipelines YAML file option</i>. 

![Existing Azure Pipelines YAML](doc_img/07.png?raw=true "Existing Azure Pipelines YAML")

* Finally, when asked for the location of the pipeline definition, select the `model_training/.pipelines/publish_aml_pipeline.yml` file and click <i>Continue</i>.

![CI YAML Pipeline Definition](doc_img/08.png?raw=true "CI YAML Pipeline Definition")

* Prior to running this pipeline, modify the values contained in `model_training/.pipelines/variable_template.yml` to reflect the names of your Azure resources and the size of your desired training cluster. We recommend provising a N-Series GPU VM for model training. The default settings included in this repo should accomodate most vision scenarios.

![Variable Template](doc_img/09.png?raw=true "Variable Template")

* Finally, when shown the pipeline review screen, click <i>Run</i>. Successful execution of this CI pipeline should publish a new pipeline in your Azure Machine Learning workspace.

![CI Pipeline Success](doc_img/10.png?raw=true "CI Pipeline Success")

* You can validate creation of the AML pipeline by first navigating to your AML workspace, then to Pipelines and Pipeline endpoints. You should see a published pipeline endpoint matching the name and description defined in `model_training/.pipelines/variable_template.yml`. This pipeline should include a single step for submitting an AutoML job.

![Azure ML Published Pipeline Endpoint](doc_img/11.png?raw=true "Azure ML Published Pipeline Endpoint")

## Step 3 - Register your Azure Storage Account used for Image Capture as an Azure Machine Learning Datastore

Inside your Azure Machine Learning workspace you can attach the Azure Storage Account, and specific containers, used for capturing images collected on the edge. This datastore can then be used to feed images into datasets used during model training.

* Navigate to your Azure Machine Learning workspace and click <i>Datastores</i>.

![Datastores](doc_img/12.png?raw=true "Datastores")

* Click <i>+ New datastore</i> and enter the required fields. For <i>Datastore name</i> choose something memorable like <i>imagestorage</i>. For authentication, your storage account key can be retrieved under the 'Access Keys' panel from the storage resource, or alternatively you can create a SAS token specific to the target container with at least Read and List permissions. Once all fields have been entered click <i>Create</i>.

![New Datastore](doc_img/13.png?raw=true "New Datastore")

* You can verify that you have successfully attached your datastore by first selecting it from the list of datastores and then clicking <i>Browse (preview)</i> - you should see images listed in the explorer which can be viewed in the right panel.

![Browse Datastore](doc_img/14.png?raw=true "Browse Datastore")

## Step 4 - Create a Labeled Dataset using the Azure Machine Learning Data Labeling Tools

Here you will use Azure ML to create a dataset of labeled images using images collected on the edge, retrieved from your attached datastore.

* Navigate to your Azure Machine Learning workspace and click <i>Data Labeling</i>.

![AML Data Labeling](doc_img/15.png?raw=true "AML Data Labeling")

* From the top menu, click <i>+ Add project</i>.

![Create AML Data Labeling Project](doc_img/16.png?raw=true "Create AML Data Labeling Project")

* Under the <i>Project details</i> section, give your project a name that is specific to the particular detection task at hand and select <i>Object Identification (Bounding Box)</i> from the menu below, then click <i>Next</i>.

![Project Details](doc_img/17.png?raw=true "Project Details")

* When prompted to select or create a dataset choose <i>+ Create dataset</i> and select the <i>From datastore</i> option.

![Create Dataset from Datastore](doc_img/18.png?raw=true "Create Dataset from Datastore")

* Give your new dataset a unique name that reflects the images captured in support of the detection task and click <i>Next</i>.



* Under datastore selection choose the datastore you added which contains images captured on the edge. Here, you can also provide a wildcarded path if you wish to pull only images from specified partitions. If you wish to pull all images from the container, enter `/` as the path.
* Confirm details about your new dataset and click `Create`.
* When prompted, choose to Enable incremental refresh at regular intervals. Thiss will automatically add newly captured images to your data labeling project.
* On the next panel, add label classes for all defects you wish to detect - include positive and negative classes here.
* You can optionally use ML-assisted labeling which will accelerate your data labeling process, particularly as more data is captured. 
* After providing all requested information click `Create project` and wait for the project to initialize. 
* Click your newly created project and then select the `Label data` button. This will open a labeling utility which will allow you to draw bounding boxes and tag defects present in your images. There are multiple keyboard shortcuts available which can be reviewed under the `Shortcut Keys` panel.
* After labeling a large number of images, navigate to the data labeling project homepage and click `Export` then select `Azure ML Dataset`. This will export your image dataset as an AutoML-compatible Azure ML dataset named according to the format 'NAME_DATE_TIME'.

## Step 5 - Train a New Object Detection Model

* First, copy the name of your newly-exported dataset to your clipboard.
* Navigate to Pipelines and then Pipeline endpoints. Select the published pipeline endpoint deployed via your CI pipeline in Azure DevOps.
* From the pipeline definition panel, click the `Submit` button. This will open a new panel with experiment details.
* For reference, experiments in Azure ML are logical collections of related runs. Here, you should either select an existing experiment, or choose to create a new experiment and provide a name.
* Under the `model_name` parameter, provide a name which will uniquely represent the model that you are training. For instance, if you are detecting presence or absence of a cap on a container, 'Cap_Detection_Model' would be an appropriate name.
* Paste the copied dataset under the `dataset_name` parameter - this dataset is retrieved programmatically during pipeline execution and used as an input to model training.
* Enter the name of a cluster to be used for model training - this cluster should already exist in your AML workspace.
* Once all fields have been entered, hit the 'Submit' button.
* Run progress can be monitored by navigating to 'Experiments' and selecting the name of your submitted experiment.
* Once training completes, the best performing model will be added to your registry automatically along with key performance metrics (Mean Average Precision, Precision, Recall). A serialized version of this model and associated python scoring file are included as well.
* Your custom trained object detection model is ready to be deployed to the edge! 
