from common import Common

class ImportFeature:
    def __init__(self, iface, sourceLayer, destinationLayer):
        self.iface = iface
        self.sourceLayer = sourceLayer
        self.destinationLayer = destinationLayer
        self.run()

    def run(self):
        pass
        #Common().popup('run import feature')