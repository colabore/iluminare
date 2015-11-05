const Rx = require('rx');
const Observable = Rx.Observable;
const React = require('react');
const MaterialUI = require('material-ui');
const List = MaterialUI.List;
const ListItem = MaterialUI.ListItem;
const injectTapEventPlugin = require("react-tap-event-plugin");
injectTapEventPlugin();

const events = require('../../utils/events');
const requests = require('../../requests');

const BUTTON = 'it-button';

function toListItem(instanciatratamento) {
  return (
    <ListItem
      className={BUTTON}
      id={instanciatratamento.id}
      key={instanciatratamento.id}
      secondaryText={instanciatratamento.data}>
      {instanciatratamento.tratamento.descricao_basica}
    </ListItem>
  );
};

function toHtml(data) {
  const items = data.instanciatratamento;
  const listItems = items.map(toListItem);
  const isEmpty = items.length == 0;
  return (
    <div>
      <h4>Tratamentos em progresso</h4>
      <span style={{'display': isEmpty ? 'block' : 'none'}}>
        <p>Nenhum tratamento foi aberto hoje.</p>
        <p><a href="/#/tratamento">Inicie as atividades</a> de pelo menos um tratamento</p>
      </span>
      <List>
        {listItems}
      </List>
    </div>
  )
};

const clicked$ = events.eventFromClass('click', BUTTON).map(x => x.id);
const html$ = requests.requestInstanciaTratamento(new Date()).map(toHtml);

clicked$.subscribe(function (id) {
  document.location = document.location.origin + '/app/#/atendimentos/' + id;
});

module.exports = html$;
