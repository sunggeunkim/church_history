from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom adapter to populate profile fields from Google OAuth data."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.display_name = data.get("name", "")
        extra_data = sociallogin.account.extra_data
        user.avatar_url = extra_data.get("picture", "")
        return user
