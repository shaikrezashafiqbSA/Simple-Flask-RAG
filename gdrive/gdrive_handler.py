import gspread
import pandas as pd
import numpy as np
import json

class GspreadHandler:
    def __init__(self, 
                #  credentials_filepath='./gdrive/lunar-landing-389714-369d3f1b2a09.json',
                 credentials_filepath='./gdrive/caramel-clock-418606-7475ecc43656.json'
                 ):
        self.credentials_filepath = credentials_filepath
        self.gc = gspread.service_account(filename=self.credentials_filepath)

    def get_sheet(self, sheet_name, worksheet_name):
        """
        Get a worksheet from a Google Sheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Returns:
            gspread.Worksheet: The worksheet object.
        """
        sh = self.gc.open(sheet_name).worksheet(worksheet_name)
        return sh
    
    def get_row_by_timestamp(self, sheet_name, worksheet_name, timestamp):
        """
        Retrieves a specific row from the Google Sheet based on a given timestamp (in string format).

        Args:
            sheet_name (str): Name of the Google Sheet.
            worksheet_name (str): Name of the worksheet within the Google Sheet.
            timestamp (str): The timestamp value (as a string) to search for.

        Returns:
            dict or None: The row data as a dictionary if found, otherwise None.
        """
        worksheet = self.get_sheet(sheet_name, worksheet_name)
        df = pd.DataFrame(worksheet.get_all_records())
        print(df["timestamp"].iloc[-1])
        test = df["timestamp"].iloc[-1]
        str_timestamp = f"{str(timestamp)}"
        print(str_timestamp)
        print(f"{test} vs {str_timestamp}")
        print(type(test), type(str_timestamp))
        if 'timestamp' in df.columns:
            # Assuming the timestamp column is already in string format
            # No need for type conversion here.
            matching_row = df.loc[df['timestamp'].str.lower() == str_timestamp.lower()]
            print(matching_row)
            if not matching_row.empty:
                return matching_row.to_dict(orient='records')[0] # Return as dict

        return None  # Return None if no matching row is found
    
    def get_cell_value(self, sheet_name, worksheet_name, cell_col_row='A1'):
        """
        Get the value of a cell in a Google Sheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            cell_col_row (str, optional): The cell address (e.g., 'A1'). Defaults to 'A1'.

        Returns:
            str: The value of the cell.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        return sh.acell(cell_col_row).value

    def update_cell(self, data, sheet_name, worksheet_name, cell_col_row='A1'):
        """
        Update a cell in a Google Sheet with new data.

        Args:
            data (str): The data to be written to the cell.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            cell_col_row (str, optional): The cell address (e.g., 'A1'). Defaults to 'A1'.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        sh.update(cell_col_row, data)
        print(f"Data written to '{sheet_name}' - '{worksheet_name}' - '{cell_col_row}'")

    def update_cols(self, data, sheet_name, worksheet_name):
        """
        Update columns in a Google Sheet with data from a DataFrame.

        Args:
            data (pd.DataFrame): The DataFrame containing the data to be written.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Raises:
            ValueError: If the columns in the DataFrame do not match the columns in the worksheet.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        existing_columns = sh.row_values(1)

        if not all(column in existing_columns for column in data.columns):
            raise ValueError("The columns in the DataFrame do not match the columns in the worksheet.")

        data_list = data.values.tolist()
        next_row = len(sh.col_values(1)) + 1
        sh.update(f'A{next_row}', data_list)
        print(f"Data appended to '{sheet_name}' - '{worksheet_name}'")

    # def update_cols(self, data, sheet_name, worksheet_name):
    #     """
    #     Update matching columns in a Google Sheet with data from a DataFrame,
    #     leaving other columns untouched.

    #     Args:
    #         data (pd.DataFrame): The DataFrame containing the data to be written.
    #         sheet_name (str): The name of the Google Sheet.
    #         worksheet_name (str): The name of the worksheet within the Google Sheet.
    #     """
    #     sh = self.get_sheet(sheet_name, worksheet_name)
    #     existing_columns = sh.row_values(1)

    #     # Find overlapping columns
    #     matching_columns = [col for col in data.columns if col in existing_columns]

    #     # If no matching columns are found, raise an error (optional)
    #     if not matching_columns:
    #         raise ValueError("No matching columns found between DataFrame and worksheet.")
        
    #         # Prepare data for updating (handle various data types)
    #     data_to_update = []
    #     for row in data[matching_columns].values.tolist():
    #         new_row = []
    #         for val in row:
    #             if isinstance(val, (np.float32, np.float64)):  # Handle NumPy floats
    #                 new_row.append(float(val))  # Convert to standard Python float
    #             elif isinstance(val, float):
    #                 if np.isnan(val):
    #                     new_row.append("")
    #                 elif val > 1e308 or val < -1e308:
    #                     new_row.append(str(val)) 
    #                 else:
    #                     new_row.append(val)
    #             else:
    #                 new_row.append(val)
    #         data_to_update.append(new_row)
    #     # Create a list of column indices for the matching columns
    #     column_indices = [existing_columns.index(col) + 1 for col in matching_columns]

    #     # Prepare data for updating (only the matching columns)
    #     data_to_update = data[matching_columns].values.tolist()

    #     # Start updating from the next available row
    #     next_row = len(sh.col_values(1)) + 1

    #     # Update each matching column individually (create Cell objects)
    #     cell_list = []
    #     for col_idx, col_data in zip(column_indices, zip(*data_to_update)):
    #         for row_idx, value in enumerate(col_data):
    #             cell_list.append(gspread.Cell(row=next_row + row_idx, col=col_idx, value=value))

    #     sh.update_cells(cell_list)  # Pass the list of Cell objects

    #     print(f"Data appended to '{sheet_name}' - '{worksheet_name}' (matching columns only)")

    def update_cols(self, data, sheet_name, worksheet_name):
        """
        Update matching columns in a Google Sheet with data from a DataFrame,
        handling data types that might cause issues with JSON serialization.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        existing_columns = sh.row_values(1)

        # Find overlapping columns
        matching_columns = [col for col in data.columns if col in existing_columns]

        if not matching_columns:
            raise ValueError("No matching columns found between DataFrame and worksheet.")

        # Prepare data for updating (handle various data types)
        data_to_update = data[matching_columns].copy()  # Create a copy to avoid modifying original DataFrame
        
        # Convert any problematic types
        for col in data_to_update.columns:
            if data_to_update[col].dtype in [np.float32, np.float64]:
                data_to_update[col] = data_to_update[col].astype(float)

        # Fill NaNs with empty strings
        data_to_update = data_to_update.fillna('')

        # Create a list of column indices for the matching columns
        column_indices = [existing_columns.index(col) + 1 for col in matching_columns]

        # Start updating from the next available row
        next_row = len(sh.col_values(1)) + 1

        # Update each matching column individually (create Cell objects)
        cell_list = []
        for col_idx, col_name in zip(column_indices, matching_columns):
            col_data = data_to_update[col_name].tolist()  # Get values from the updated DataFrame
            for row_idx, value in enumerate(col_data):
                cell_list.append(gspread.Cell(row=next_row + row_idx, col=col_idx, value=value))

        sh.update_cells(cell_list)

        print(f"Data appended to '{sheet_name}' - '{worksheet_name}' (matching columns only)")


    def append_column(self, data, sheet_name, worksheet_name, column='A'):
        """
        Append data to the next empty row in a specified column.

        Args:
            data (str): The data to append.
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
            column (str, optional): The column to append the data to. Defaults to 'A'.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        next_row = len(sh.col_values(ord(column) - ord('A') + 1)) + 1
        sh.update(f'{column}{next_row}', [[data]])
        print(f"Data '{data}' appended to column '{column}' in '{sheet_name}' - '{worksheet_name}'")

    def clear_sheet(self, sheet_name, worksheet_name):
        """
        Clear the data in a Google Sheet worksheet.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        sh.clear()
        print(f"Data cleared from '{sheet_name}' - '{worksheet_name}'")

    def get_sheet_as_df(self, sheet_name, worksheet_name):
        """
        Get the entire data from a Google Sheet worksheet as a pandas DataFrame.

        Args:
            sheet_name (str): The name of the Google Sheet.
            worksheet_name (str): The name of the worksheet within the Google Sheet.

        Returns:
            pd.DataFrame: The worksheet data as a DataFrame.
        """
        sh = self.get_sheet(sheet_name, worksheet_name)
        data = sh.get_all_values()
        headers = data.pop(0)
        df = pd.DataFrame(data, columns=headers)
        return df