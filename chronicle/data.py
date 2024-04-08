from chronicle.chronicle import logger


class Data:
    """Data holder for Bungie API results."""

    def __init__(self, title, *args, columns=None):
        self._data = []
        self._index = 0
        self._raw_data = args
        self.columns = columns if columns else []
        self.title = title

        for arg in args:
            self.add(arg)

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return self

    def __len__(self):
        return len(self._data)

    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration

        self._index += 1
        return self._data[self._index - 1]

    def __repr__(self):
        return f"Columns: {self.columns}"

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, new_columns):
        self._columns = new_columns

    @property
    def has_data(self):
        return len(self._data) > 0

    @staticmethod
    def f(a, b):
        """Filters a based on b."""
        return [i for i in a if i in b]

    def add(self, data, columns=None):
        """Adds to data."""
        if len(data) == 0:
            raise Exception("Cannot add data of 0 length.")

        # Add additional columns. Otherwise, this add operation will use the existing columns.
        columns = columns if columns is not None else []
        self.columns += columns

        if type(data[0]) is dict:
            # This is a dictionary.
            self.add_dict(data)
        else:
            # Assume this is an object.
            self.add_obj(data)

    def join(self, data, columns=None):
        """Joins to data."""
        logger.debug("Joining data", data=data, columns=columns)

        if len(data) == 0:
            raise Exception("Cannot join data of 0 length.")

        if self.has_data and len(data) != len(self):
            raise Exception("Cannot join two datas of different lengths.")

        if type(data[0]) is dict:
            self.join_dict(data, columns)
        else:
            self.join_obj(data, columns)

    def add_dict(self, data):
        """Adds a dict."""
        # Determine the columns that will be used to add new data entries. This is either a
        # combination of new columns and existing ones, just existing ones, or everything in data.
        dict_keys = list(next(iter(data)).keys())
        columns = Data.f(dict_keys, self.columns) if self.columns else dict_keys

        # In the event that columns has been None so far, we know initialize it based on this add.
        self.columns = self.columns if self.columns else columns

        # Add data.
        for d in data:
            self._data.append([v for k, v in d.items() if k in columns])

    def add_obj(self, data):
        """Adds an object."""
        # Determine the columns that will be used to add new data entries. This is either a
        # combination of new columns and existing ones, just existing ones, or everything in data.
        obj_attrs = [attr for attr in dir(data[0]) if not attr.startswith("_")]
        columns = Data.f(obj_attrs, self.columns) if self.columns else obj_attrs

        # In the event that columns has been None so far, we know initialize it based on this add.
        self.columns = self.columns if self.columns else columns

        # Add data.
        for d in data:
            self._data.append([getattr(d, column) for column in columns])

    def join_dict(self, data, columns=None):
        """Joins a dict with existing items."""
        # Update the existing columns with new columns.
        dict_keys = list(next(iter(data)).keys())
        self.columns += Data.f(dict_keys, columns) if columns else dict_keys

        # Capture whether or not there is initial data before adding any.
        has_data = self.has_data

        # Update existing data with new fields.
        for i, d in enumerate(data):
            next_data = [v for k, v in d.items() if k in self.columns]
            if has_data:
                # This has data we are joining into.
                self._data[i] += next_data
            else:
                # We are joining into the void, so just take the data as-is.
                self._data.append(next_data)

    def join_obj(self, data, columns=None):
        """Joins an object with existing items."""
        # Update the existing columns with new columns.
        obj_attrs = [attr for attr in dir(data[0]) if not attr.startswith("_")]
        self.columns += Data.f(obj_attrs, columns) if columns else obj_attrs

        # Capture whether or not there is initial data before adding any.
        has_data = self.has_data

        # Update existing data with new fields.
        for i, d in enumerate(data):
            next_data = [getattr(d, attr) for attr in obj_attrs if attr in self.columns]
            if has_data:
                # This has data we are joining into.
                self._data[i] += next_data
            else:
                # We are joining into the void, so just take the data as-is.
                self._data.append(next_data)
