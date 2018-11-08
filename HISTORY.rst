=======
History
=======

0.0.8 (2018-06-26)
------------------

* Relay MT messages

0.0.4 (2017-10-13)
------------------

* Optional external procedure to handle received messages.

0.0.2 (2017-08-28)
------------------

* Parse MT messages in any order. Altough it usually comes in the same order, with the payload in the end, there is no restriction in the documentation imposing that.
* Refactoring the parsing process.
* Handling inbound (MO) and outbound (MT) DirectIP transmissions.

0.0.1 (2017-07-03)
------------------

* Only receiving DirectIP transmissions.
* Acknowledge to iridium gateway when receive a proper message.
* Logging.
* Command line to run server.
* Class to parse isbd messages.
