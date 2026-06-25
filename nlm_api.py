import requests


def fetch_icd_description(code):
    """
    Fetch an ICD-10 diagnosis description from the
    National Library of Medicine (NLM) Clinical Tables API.

    Args:
        code (str): ICD-10 code (e.g. K35.8)

    Returns:
        str | None:
            - Diagnosis description if found
            - None if not found or an error occurs
    """

    try:
        code = code.strip().upper()

        url = (
            "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            f"?terms={code}&sf=code,short_desc"
        )

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        if (
            data
            and len(data) > 3
            and data[3]
            and len(data[3][0]) > 1
        ):
            return data[3][0][1]

        return None

    except requests.exceptions.Timeout:
        print("NLM API Error: Request timed out.")
        return None

    except requests.exceptions.ConnectionError:
        print("NLM API Error: Connection failed.")
        return None

    except requests.exceptions.RequestException as e:
        print(f"NLM API Error: {e}")
        return None

    except (IndexError, KeyError, TypeError):
        print("NLM API Error: Unexpected response format.")
        return None


if __name__ == "__main__":
    test_code = input("Enter ICD-10 Code: ")

    description = fetch_icd_description(test_code)

    if description:
        print(f"\nDiagnosis: {description}")
    else:
        print("\nNo diagnosis found.")