
function goTo(route) {
  document.location = document.location.origin
    + document.location.pathname + '#' + route;
}

module.exports = {
  goTo: goTo
}
