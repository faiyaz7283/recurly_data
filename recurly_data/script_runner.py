"""Script Runner."""
import os
import pickle
from typing import Dict, List, Optional, Union


class ScriptRunner:
    """Class Script Runner."""

    def __init__(
            self,
            data_obj: dict,
            data_file: Optional[str] = None,
            info_file: str = "info.pickle",
    ):
        self.info_file = info_file
        self.data_obj = data_obj
        self.data_file = data_file


    def continue_extraction(self):
        if self.data_file and os.path.exists(self.data_file):
            with open(self.filename, "rb") as f:
                # Read first line for columns
                columns = f.readline().decode().strip().split(",")
                # Read second line as first row
                first_row = f.readline().decode().strip().split(",")
                # Jump to the second last byte.
                f.seek(-2, os.SEEK_END)
                # Until EOL is found...
                while f.read(1) != b"\n":
                    # jump back the read byte plus one more.
                    f.seek(-2, os.SEEK_CUR)
                # Read last line.
                last_row = f.readline().decode().strip().split(",")
            first = dict(zip(columns, first_row))
            last = dict(zip(columns, last_row))
            self.last_row = last
            frst_ct = float(first["created_at"])
            lst_ct = float(last["created_at"])
            self.total_extracted = int(last["row"])
            last_created_at = datetime.utcfromtimestamp(lst_ct).isoformat()
            if frst_ct > lst_ct:
                # Last iteration ran in desc order, so update end_time.
                self.end_time = last_created_at
            else:
                # Last iteration ran in asc order, so update begin_time.
                self.begin_time = last_created_at

    @property
    def info(self):
        """Script info."""
        data = {}
        if os.path.exists(self.info_file):
            with open(self.info_file, "rb") as handle:
                data = pickle.load(handle)
        return data

    @info.setter
    def info(self, data: dict):
        if self.info:
            data.update(self.info)
        with open(self.info_file, "wb") as handle:
            pickle.dump(
                data, handle, protocol=pickle.HIGHEST_PROTOCOL
            )
