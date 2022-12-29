# Solarman Logger #

Solarman Wifi Logger to mqtt for Home Assistant.

## About ##

Directly read DEYE Inverter (and clones, Sunsynk, Ohm etc.) statistics through the locally accessible Solarman Logger and send the values to a MQTT server.

### run_inverter_queries script forever

```
 ./run_inverter_queries.sh > run_inverter_queries.log 2>&1 & 
```