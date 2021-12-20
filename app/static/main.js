
// Cuando se pulsa el boton de modo noche activamos o desactivamos el modo noche y lo guardamos en localStorage
const btnSwitch = document.querySelector('#switch');

btnSwitch.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  btnSwitch.classList.toggle('active');

  if(document.body.classList.contains('dark')){
    localStorage.setItem('dark-mode', 'true');
  } else{
    localStorage.setItem('dark-mode', 'false');
  }
});

// Obtenemos el modo a traves de localstorage

if(localStorage.getItem('dark-mode') == 'true'){
    document.body.classList.add('dark');
    btnSwitch.classList.add('active');
} else {
    document.body.classList.remove('dark');
    btnSwitch.classList.remove('active');
}


//Cuando se cargue la primera vez la pagina de pokemons añadir todas las filas

$( document ).ready(function(){
  var fila = $('#fila')

  $.ajax({
    type:'GET',
    url: 'http://127.0.0.1:5000/api/pokemons',
    success:function(pokemons){
      $.each(pokemons, function(i, pok){
        fila.append(`<tr><td><img src="${pok.img}" width="100px" />` + '</td><td>' + pok.name + '</td><td>' + pok.tipo+ '</td><td>' + pok.altura + '</td><td>' + pok.peso + '</td><td>' +pok.debilidad + '</td></tr>')
      });
    }
  });
});



// Cuando cambiemos el select añadimos las filas de la peticion por tipo
  $('#poke_busqueda').change(function(){
    let value = $(this).val()
    var request_url = 'http://127.0.0.1:5000/api/pokemons?tipo=' + value
    var fila = $('#fila')

    //Para cuando se seleccione Cualquiera
    if(value == "Todos"){
      request_url = 'http://127.0.0.1:5000/api/pokemons'
    }

    $.ajax({
      type:'GET',
      url: request_url,
      success:function(pokemons){
        // Antes de añadir, borramos lo que habia
        var div = document.getElementById('fila');
        while (div.firstChild) {
            div.removeChild(div.firstChild);
        }
        $.each(pokemons, function(i, pok){
          fila.append(`<tr><td><img src="${pok.img}" width="100px" />` + '</td><td>' + pok.name + '</td><td>' + pok.tipo+ '</td><td>' + pok.altura + '</td><td>' + pok.peso + '</td><td>' +pok.debilidad + '</td></tr>');
        });
      }
    });
  });



  // Cuando pulsemos el boton de borrar, quitamos lo que habia y añadimos los datos y el boton para confirmar el borrado
  $('.Borrado').click(function(){
     let value = $(this).val()
      var request_url = 'http://127.0.0.1:5000/api/pokemons/' + value
      $.ajax({
        url: request_url,
        type:'GET',
        success:function(pok){
          var div = document.getElementById('tabla_borrado');
          while (div.firstChild) {
             div.removeChild(div.firstChild);
          }
          $("#f_borrar").append('<li> Nombre: ' + pok.name + '</li><li> Tipo: ' + pok.tipo + '</li><li>Altura: ' + pok.altura +'</li><li>Peso: ' + pok.peso + '</li><li>Debilidad: ' + pok.debilidad + '</li><li><img src=" ' + pok.img + '" width="200px"></li><br> <form action="/modificarpokemon" method="post"><input type="hidden" name="id" value="' + value + '" /><input name="accion" value="Confirmar borrado" type="submit" class="btn btn-primary"></button></form>' )
        }
      });

    });

//Funciones para el mapa

//Creamos el mapa
let map = L.map('map').fitWorld();
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

//Creamos los iconos que usaremos para cada pokemon
var icono = new L.Icon({
  iconUrl: 'https://image.flaticon.com/icons/svg/854/854866.svg',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconPikachu = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/025.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconSquirtle = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/007.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconBulbasaur = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/001.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconCharmander = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/004.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconMagikarp = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/129.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

var iconSnorlax = new L.Icon({
  iconUrl: 'https://assets.pokemon.com/assets/cms2/img/pokedex/full/143.png',
  iconSize: [50, 50],
  iconAnchor: [25, 50]
});

//Cuando cambie el select, obtenemos las coordenadas y dependiendo del pokemon usamos su icono
document.getElementById('select-location').addEventListener('change', function(e){

      let coords = e.target.value.split(",");

      if(e.target.value == "40.748433, -73.985656"){
          L.marker(coords,{icon: iconPikachu}).addTo(map)

      } else if(e.target.value == "-0.600737, 73.080630"){
        L.marker(coords,{icon: iconSquirtle}).addTo(map)

      } else if(e.target.value == "-2.645939, -62.783359"){
        L.marker(coords,{icon: iconBulbasaur}).addTo(map)

      } else if(e.target.value == "24.555448, 54.449169"){
        L.marker(coords,{icon: iconCharmander}).addTo(map)

      } else if(e.target.value == "36.712376, -3.700226"){
        L.marker(coords,{icon: iconMagikarp}).addTo(map)

      } else if(e.target.value == "37.197021, -3.624433"){
        L.marker(coords,{icon: iconSnorlax}).addTo(map)
      } else{
       L.marker(coords,{icon: icono}).addTo(map)
     }
      map.flyTo(coords, 18);
    });
