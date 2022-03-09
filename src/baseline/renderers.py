from rest_framework.renderers import JSONRenderer


class EnvelopeJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            return

        # create the envelope when this isn't a paginated response, which is in itself an envelope
        if "results" not in data:
            # create a copy of the data as the result and clear out the
            # existing dictionary in order to continue referencing the
            # same object that's referenced in the upstream Response object
            enveloped_data = {"result": data.copy()}

            if isinstance(data, dict):
                data.clear()
                data.update(enveloped_data)
            else:
                data = enveloped_data

        rendered = super().render(data, accepted_media_type, renderer_context)

        return rendered
