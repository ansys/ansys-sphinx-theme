"""This is assets module."""
import os

# get location of this directory
_this_path = os.path.dirname(os.path.realpath(__file__))


api = os.path.join(_this_path, "index_api.png")
contribute = os.path.join(_this_path, "index_contribute.png")
getting_started = os.path.join(_this_path, "index_getting_started.png")
user_guide = os.path.join(_this_path, "index_user_guide.png")

__all__ = ["api", "contribute", "getting_started", "user_guide"]
