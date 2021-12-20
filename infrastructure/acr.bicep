@description('The name of the Azure container registry.')
param acrName string

resource azureContainerRegistry 'Microsoft.ContainerRegistry/registries@2020-11-01-preview' = {
  name: acrName
  location: resourceGroup().location
  sku: {
    name: 'Premium'
  }
  properties: {
    adminUserEnabled: true
    publicNetworkAccess: 'Enabled'
    networkRuleSet: {
      defaultAction: 'Allow'
    }
  }
}

// Private endpoints are created in post-deploy stage

output acrName string = azureContainerRegistry.name
output acrLoginServer string = azureContainerRegistry.properties.loginServer
