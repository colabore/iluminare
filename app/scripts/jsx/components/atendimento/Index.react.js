var React = require('react');
var Router = require('react-router'),
  RouteHandler = Router.RouteHandler;
var MaterialUI = require('material-ui'),
  ThemeManager = new MaterialUI.Styles.ThemeManager(),
  Card = MaterialUI.Card,
  CardTitle = MaterialUI.CardTitle,
  CardText = MaterialUI.CardText,
  CardActions = MaterialUI.CardActions,
  IconButton = MaterialUI.IconButton,
  CardMedia = MaterialUI.CardMedia;

var Atendimento = React.createClass({
  childContextTypes: {muiTheme: React.PropTypes.object},
  getChildContext: function() {return {muiTheme: ThemeManager.getCurrentTheme()}},
  render: function () {
    return (
      <div>
        <h1>Atendimento</h1>
        <RouteHandler />
      </div>
    )
  }
});

module.exports = Atendimento;
