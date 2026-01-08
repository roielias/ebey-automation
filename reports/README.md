# Reports Directory

This directory contains test execution reports.

## Sample Reports Included

- `sample_report.html` - Example HTML report from pytest-html
- `allure_report_screenshot.png` - Screenshot of Allure report dashboard

## Generating Full Reports

To generate complete test reports, run:

```bash
# HTML Report
pytest tests/ --html=reports/report.html --self-contained-html

# Allure Report
pytest tests/ --alluredir=allure-results
allure serve allure-results
```

## Report Types

1. **HTML Report** - Single file HTML report with test results
2. **Allure Report** - Interactive web-based report with detailed analytics
3. **Logs** - Detailed execution logs in `logs/` directory

**Note:** Full reports are generated during test execution and are not committed to Git to keep repository size small.
