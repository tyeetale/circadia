# Resources & Research

Useful references for building and maintaining Circadia.

## Official Fitbit API

- [Fitbit Developer Portal](https://www.fitbit.com/dev) - Create and manage OAuth apps
- [Fitbit Web API Documentation](https://dev.fitbit.com/build/reference/web-api/)
- [Python Fitbit Library](https://python-fitbit.readthedocs.io/en/latest/) - Popular Python wrapper for Fitbit API

## Alternative Implementations

- [yukikitayama/fitbit](https://github.com/yukikitayama/fitbit) - Another Python Fitbit implementation
- [arpanghosh8453/fitbit-grafana](https://github.com/arpanghosh8453/fitbit-grafana) - Original project this was based on (InfluxDB + Grafana)

## Fitbit API Endpoints Reference

### Heart Rate
- `GET /1/user/-/activities/heart/date/{date}/1d/{detail-level}.json` - Intraday heart rate
- `GET /1/user/-/activities/heart/date/{start-date}/{end-date}.json` - Heart rate zones

### Activity
- `GET /1/user/-/activities/tracker/{metric}/date/{start-date}/{end-date}.json` - Activity minutes, steps, calories, distance
- `GET /1/user/-/activities/active-zone-minutes/date/{start-date}/{end-date}.json` - Active zone minutes

### Sleep
- `GET /1.2/user/-/sleep/date/{start-date}/{end-date}.json` - Sleep log

### HRV & Biometrics
- `GET /1/user/-/hrv/date/{start-date}/{end-date}.json` - Heart rate variability
- `GET /1/user/-/spo2/date/{start-date}/{end-date}.json` - SPO2
- `GET /1/user/-/br/date/{start-date}/{end-date}.json` - Breathing rate
- `GET /1/user/-/temp/skin/date/{start-date}/{end-date}.json` - Skin temperature

### Body
- `GET /1/user/-/body/log/weight/date/{start-date}/{end-date}.json` - Weight/BMI

### Devices
- `GET /1/user/-/devices.json` - Device info and battery level
- `GET /1/user/-/profile.json` - User profile (timezone, etc.)

## Rate Limits

- **150 API calls per hour** (per user)
- Rate limit resets every hour
- Intraday data limited to 24 hours per API call

## Fitbit OAuth Notes

- Application type must be **"Personal"** for intraday data access
- Requires refresh token flow (access tokens expire)
- Redirect URL can be localhost for development

## Similar Projects

- [garmin-grafana](https://github.com/arpanghosh8453/garmin-grafana) - Sister project for Garmin devices
- [Oura Ring integration](https://github.com/) - Similar concept for Oura data (search for "oura python")
- [Whoop API](https://github.com/) - Whoop integration (search for "whoop python api")

## ML/Health Resources

- [HRV Analysis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5624990/) - Scientific paper on HRV interpretation
- [Sleep Scoring Algorithms](https://www.ncbi.nlm.nih.gov/) - Research on sleep quality scoring

---

*Last updated: February 2026*
