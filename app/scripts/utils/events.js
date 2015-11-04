const Rx = require('rx'),
  Observable = Rx.Observable;

function eventFromClass(eventName, className) {
  return Observable.fromEvent(document, eventName)
    .map(x =>x.path.filter(y => y.className === className))
    .filter(x =>x && x.length == 1)
    .map(x => x.pop());
}

module.exports = {
  eventFromClass: eventFromClass
}
