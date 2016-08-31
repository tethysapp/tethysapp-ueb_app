from tethys_sdk.base import TethysAppBase, url_map_maker


class UebApp(TethysAppBase):
    """
    Tethys app class for Ueb App.
    """

    name = 'Utah Energy Balance Model App'
    index = 'ueb_app:home'
    icon = 'ueb_app/images/ueb.png'
    package = 'ueb_app'
    root_url = 'ueb-app'
    color = '#99ccff'
    description = 'UEB APP description'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
                    # url for app
                    UrlMap(name='home',
                           url='ueb-app',
                           controller='ueb_app.controllers.home'),
                    UrlMap(name='model_input',
                           url='ueb-app/model_input',
                           controller='ueb_app.controllers.model_input'),
                    UrlMap(name='model_input_submit',
                           url='ueb-app/model_input/model_input_submit',
                           controller='ueb_app.controllers.model_input_submit'),
                    UrlMap(name='model_run',
                           url='ueb-app/model_run',
                           controller='ueb_app.controllers.model_run'),

                    # testing url
                    UrlMap(name='test',
                           url='ueb-app/test',
                           controller='ueb_app.controllers.test'),
                    UrlMap(name='test_submit',
                           url='ueb-app/test/test_submit',
                           controller='ueb_app.controllers.test_submit'),
        )

        return url_maps