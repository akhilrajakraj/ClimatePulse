
## Pipeline Reliability and Testing

ClimatePulse includes automated tests to verify
data quality and pipeline reliability.

### Data Validation
- Required metadata validation
- Hourly field validation
- Data type validation
- Array length consistency
- Empty timestamp detection

### API Failure Handling
- API timeout simulation
- HTTP error simulation
- Invalid JSON response handling
- Missing hourly data handling

### Pipeline Failure Protection
- Verify extraction failure propagation
- Ensure validation is not executed after extraction failure
- Prevent raw data storage after extraction failure
- Prevent transformation after extraction failure
- Prevent CSV generation after extraction failure

### Running Tests

Install pytest:

```bash
python -m pip install pytest
```

Run all tests:

```bash
python -m pytest -v
```

Current test suite: 13 passing tests.
