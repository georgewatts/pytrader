# pytrader
**DEMO ONLY**

Basic implementation of a FOREX market reader in Python.

Implements lightstreamer to contact IG's API found [here](https://labs.ig.com). Also uses wxPython to manage the GUI interface.

**ONLY TESTED ON MAC OS X**

## Using pytrader
1. Clone or download the repository
2. Modify the following line in `main.py`:
```python
self.broker = IGBroker(username, password)
```
to include your username and password registered with IG trading.

3. Navigate to the directory and run:
```shell
$ python main.py
```

## Screenshots
![alt text](https://github.com/georgewatts/pytrader/blob/master/images/Browse%20Markets.png?raw=true "Browse Markets")
![alt text](https://github.com/georgewatts/pytrader/blob/master/images/Live%20Markets.png?raw=true "Live Markets")

## Acknowledgements
The lightstreamer code originated from the [Lightstreamer github](https://github.com/Lightstreamer/Lightstreamer-example-StockList-client-python) complete with examples not limited to Python.
