import pickle

import misp_lib_stix2

from .constants import IDENTITY_ID


def test_pickling():
    """
    Ensure a pickle/unpickle cycle works okay.
    """
    identity = misp_lib_stix2.v20.Identity(
        id=IDENTITY_ID,
        name="alice",
        description="this is a pickle test",
        identity_class="individual",
    )

    pickle.loads(pickle.dumps(identity))
