// Configurable input parameters
@description('The environment suffix to append to resource names.')
param environmentSuffix string = 'ci'

@description('The environment prefix to append to resource names.')
param environmentName string = 'computer-vision'

@description('The environment prefix to append to resource names.')
param environmentNameShort string = 'computervision'

// Resource names
var acrResourceName = '${environmentName}acr${environmentSuffix}'
var saResourceName = '${environmentNameShort}sa${environmentSuffix}'

// ACR
module azureContainerRegistry 'acr.bicep' = {
  name: 'azureContainerRegistryDeploy'
  params: {
    acrName: acrResourceName
  }
}

// IotHub
module iothub 'iot-hub.bicep' = {
  name: 'iothub'
  params: {
    environmentName: environmentName
    environmentSuffix: environmentSuffix
  }
}

// Storage Account
module sa 'storage-account.bicep' = {
  name: 'sa'
  params: {
    storageAccountName: saResourceName
  }
}

output acrName string = azureContainerRegistry.outputs.acrName
output acrLoginServer string = azureContainerRegistry.outputs.acrLoginServer
