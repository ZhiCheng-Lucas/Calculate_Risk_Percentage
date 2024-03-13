# Calculate_Risk_Percentage
 
## About This Project

This project is a Flask-based application designed for risk assessment calculations based on suspect cases from various log sources such as building access, proxy logs, and PC access. 
It incorporates a unique frequency scaling and normalization methodology to provide a nuanced and actionable risk percentage.

## Usage

### Running the Application

Navigate to the application's root directory(src directory) and run :

```bash
python app.py
```

This will start the Flask server, typically accessible at `http://localhost:5000`.

### Endpoints

- **/health**: GET request that returns the service's health status.
- **/percentage**: POST request that accepts a JSON payload with logs and returns a calculated risk percentage.

### Suspect Cases

The application categorizes suspect activities into six cases, each associated with a base risk percentage reflecting its potential impact on security:

1. **After Hour Login (10%)**: Considered low risk, usually indicating overtime work or misaligned schedules.
2. **Potential Account Sharing (20%)**: Moderate risk, suggesting unauthorized access.
3. **Terminated Employee Login (50%)**: High risk, indicating severe access control breaches.
4. **Failed Attempt to Enter Building / Potential Tailgating (15%)**: Low risk, mainly involving physical security breaches.
5. **Impossible Traveler (50%)**: High risk, suggesting account compromise.
6. **Potential Data Exfiltration (50%)**: High risk, endangering data confidentiality.

### Frequency Scaling

The application implements a scaling strategy to address the diminishing impact of repeated incidents. Inspired by logarithmic time complexity, this method halves the impact of each successive case of the same type. 

For instance, three instances of after-hour logins would cumulatively increase the risk by 17.5% (10% for the first, 5% for the second, and 2.5% for the third), emphasizing a decreasing incremental effect with each new incident.

### Normalization

To maintain coherence and prevent inflation of risk percentages, the algorithm caps the total risk score at 100%. If the cumulative percentage exceeds this threshold, it is normalized to 100%, ensuring that the risk assessment remains realistic and actionable.

### Rounding Up

The application rounds the total risk percentage to the nearest full percentage, always rounding up in the case of decimals. 
This approach ensures that any fractional risk percentage is conservatively adjusted to the next full number, reflecting a precautionary stance in risk assessment.

## Sample Input and Output

### Sample Input

The application accepts a JSON payload containing categorized logs, with each log entry detailing an event and specifying a `suspect` value that corresponds to one of the predefined suspect cases. Below is a sample input consisting of building access and proxy log records:

```json
{
    "building_access": [
        {
            "id": 28230,
            "user_id": 696,
            "access_date_time": "2023-01-15 03:43:14.000000",
            "direction": "OUT",
            "status": "FAIL",
            "office_location": "Beijing",
            "suspect": 4
        },
        {
            "id": 28230,
            "user_id": 696,
            "access_date_time": "2023-01-15 03:43:14.000000",
            "direction": "OUT",
            "status": "FAIL",
            "office_location": "Beijing",
            "suspect": 4
        }
    ],
    "proxy_log": [
        {
            "id": 1349,
            "user_id": 12,
            "access_date_time": "2023-01-27 08:32:02.000000",
            "machine_name": "PC_12",
            "url": "https://resources.workable.com/tutorial/source-on-slack",
            "category": "Collaboration, Communication",
            "bytes_in": 3851864,
            "bytes_out": 87534786,
            "suspect": 6
        }
    ]
}
```

### Sample Output

Based on the input provided, the application calculates the total risk percentage using its frequency scaling and normalization approach. The output is a JSON object containing a message that indicates the completion of the risk calculation and the calculated total risk percentage:

```json
{
    "message": "Risk calculation complete.",
    "total_risk_percentage": 73
}
```

### Explanation

The input sample includes two incidents of "Failed Attempt to Enter Building / Potential Tailgating" (Suspect Case 4, base risk of 15%) and one incident of "Potential Data Exfiltration" (Suspect Case 6, base risk of 50%).

- The first incident of Case 4 contributes a 15% risk.
- The second incident of the same case has its impact halved to 7.5%, according to the frequency scaling rule.
- The incident of Case 6 contributes a 50% risk.

Adding these percentages together yields a raw total of 72.5%. Since the application rounds up fractional percentages, the final calculated risk percentage is rounded up to 73%.

### Testing

Install `pytest` and `pytest-dependency`:

```bash
pip install pytest pytest-dependency
```

Run tests with:

```bash
python -m pytest
```
in Calculate_Risk_Percentage directory

## TODO

1. **Implement Static Analysis**: Integrate static code analysis tools to identify potential security flaws, code quality issues, and other vulnerabilities within the application's codebase. Tools such as Flake8, Black for code formatting, and Bandit for security vulnerabilities are recommended.

2. **Automate Static Analysis and Testing**:
    - **Continuous Integration (CI) Pipeline**: Set up a CI pipeline using platforms like GitHub Actions, GitLab CI, or Jenkins to automate the running of static analysis and tests with each commit or pull request.
    - **Pre-commit Hooks**: Implement pre-commit hooks using a tool like `pre-commit` to run static analysis and formatting checks before each commit, helping to catch issues early in the development cycle.
