import os


class Model(object):

    def __init__(self, context):
        self._cranium_region = None
        self._mandible_teeth_region = None
        self._maxilla_teeth_region = None
        self._context = context
        self._load_models()

    def _load_models(self):
        self._load_model("cranium")
        self._load_model("maxilla_teeth")
        self._load_model("mandible_teeth")

    def _load_model(self, name):
        model_node_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models', '%s.exnode' % name)
        model_element_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models', '%s.exelem' % name)
        region = self._context.getDefaultRegion()
        setattr(self, "_%s_region" % name, region.createChild(name))
        attribute = getattr(self, "_%s_region" % name)
        attribute.readFile(model_node_file)
        attribute.readFile(model_element_file)

    def get_context(self):
        return self._context

    def get_cranium_region(self):
        return self._cranium_region

    def get_mandible_teeth_region(self):
        return self._mandible_teeth_region

    def get_maxilla_teeth_region(self):
        return self._maxilla_teeth_region
