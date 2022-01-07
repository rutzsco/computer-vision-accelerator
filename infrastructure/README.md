# Computer Vision Accelerator - Deploy Core Cloud Services

Set up a CI pipeline inside of Azure DevOps to deploy the cloud services for supporting computer vision on Azure IotEdge.

## Azure Resources

- Iot Hub
- Storage Account
- Container Registry
- Azure SQL Database
- Stream Analytics(TBD)

## IaC and Deployment Pipeline

The bicep IaC files and azure devops deployment pipeline are located in the infrastructure folder. The following steps for creating the deployment pipeline in ADO:

![1. Create New Pipeline](doc_img/createpipelinestep1 "Create New Pipeline")
![2. Select Repo](doc_img/createpipelinestep2 "Select Repo")
![3. Selecte existing Azure Pipelines YAML File](doc_img/createpipelinestep3 "Selecte existing pipeline")
![4. Select YAML Pipeline](doc_img/createpipelinestep4 "Select YAML Pipeline")

## Reference



