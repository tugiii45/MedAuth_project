import requests


def fetch_icd_description(code):
    """
    Looks up an ICD-10 code and returns its diagnosis description.

    Args:
        code (str): The ICD-10 diagnosis code entered by the user.

    Returns:
        str | None:
            Returns the diagnosis description if found,
            otherwise returns None.
    """

    try:
        # Remove extra spaces and convert the code to uppercase
        code = code.strip().upper()

        # Build the API request URL
        url = (
            "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            f"?terms={code}&sf=code,short_desc"
        )

        # Send a request to the NLM API
        response = requests.get(url, timeout=5)

        # Raise an error if the request was unsuccessful
        response.raise_for_status()

        # Convert the API response into JSON format
        data = response.json()

        # Check whether a matching diagnosis was returned
        if (
            data
            and len(data) > 3
            and data[3]
            and len(data[3][0]) > 1
        ):
            # Return the diagnosis description
            return data[3][0][1]

        # Return None if no diagnosis was found
        return None

    # Handle a request timeout
    except requests.exceptions.Timeout:
        print("NLM API Error: Request timed out.")
        return None

    # Handle connection problems
    except requests.exceptions.ConnectionError:
        print("NLM API Error: Connection failed.")
        return None

    # Handle other request-related errors
    except requests.exceptions.RequestException as e:
        print(f"NLM API Error: {e}")
        return None

    # Handle unexpected API response formats
    except (IndexError, KeyError, TypeError):
        print("NLM API Error: Unexpected response format.")
        return None


# Run this section only when the file is executed directly
if __name__ == "__main__":

    # Ask the user to enter an ICD-10 code
    test_code = input("Enter ICD-10 Code: ")

    # Retrieve the diagnosis description
    description = fetch_icd_description(test_code)

    # Display the diagnosis if found
    if description:
        print(f"\nDiagnosis: {description}")
    else:
        # Display a message if no diagnosis exists
        print("\nNo diagnosis found.")