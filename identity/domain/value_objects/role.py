from enum import Enum


class Role(str, Enum):
    TENANT = "tenant"
    LANDLORD = "landlord"
    ADMIN = "admin"
