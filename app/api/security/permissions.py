class Permissions:

    ROLE_PERMISSIONS = {
        "admin": {
            "*",
        },
        "partner": {
            "chat",
            "users",
            "profiles",
        },
        "user": {
            "chat",
            "profile",
        },
    }

    def has_permission(
        self,
        role: str,
        permission: str,
    ) -> bool:

        permissions = (
            self.ROLE_PERMISSIONS.get(
                role,
                set(),
            )
        )

        return (
            "*"
            in permissions
            or permission
            in permissions
        )
