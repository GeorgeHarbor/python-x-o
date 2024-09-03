  document.addEventListener('DOMContentLoaded', function() {
    const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    let room = null;
    let player_marker = null;
    let gameActive = true;
    let currentPlayer = 'X';

    const cells = document.querySelectorAll('.cell');
    const resetButton = document.getElementById('game-reset');
    const leaveButton = document.getElementById('leave-game');

    socket.on('connect', () => {
      socket.emit('join_room_event');
    });

    socket.on('log', (data) => {
      logEvent(data.msg);
    });

    socket.on('move', (data) => {
      cells[data.index].textContent = data.player_marker;
      currentPlayer = data.next_player;
      //logEvent(`${data.player_marker} marked cell ${data.index}`);
      //checkGameStatus();
    });

    socket.on('connect_response', (data) => {
      player_marker = data.marker;
      room = data.room;
    })

    cells.forEach(cell => {
      cell.addEventListener('click', () => {
        if (gameActive && cell.textContent.trim() === '') {
          const index = cell.getAttribute('data-cell-index');
          makeMove(index);
        }
      });
    });

    //resetButton.addEventListener('click', () => {
    //  socket.emit('reset', { room });
    //});
    //
    //leaveButton.addEventListener('click', () => {
    //  socket.emit('leave', { room });
    //  window.location.href = "{{ url_for('home') }}"; 
    //});

    function makeMove(index) {
      if (player_marker === currentPlayer) {
        socket.emit('move', { index, player_marker, room });
      } else {
        //logEvent("It's not your turn!");
      }
    }
    const logEvent = (msgs) => {
      document.getElementById('game-log-list').innerHTML = '';
      msgs.forEach((msg) => {
        const p = document.createElement('li');
        p.textContent = msg;
        document.getElementById('game-log-list').appendChild(p);
        document.getElementById('game-log-list').scrollTop = document.getElementById('game-log').scrollHeight;
      })
    }

  })

