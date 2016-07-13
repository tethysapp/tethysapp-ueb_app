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

        url_maps = (UrlMap(name='home',
                           url='ueb-app',
                           controller='ueb_app.controllers.home'),
        )

        return url_maps