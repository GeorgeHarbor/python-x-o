document.addEventListener('DOMContentLoaded', function() {
  const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
  let room = null;
  let player_marker = null;
  let username = null
  let gameActive = true;
  let currentPlayer = 'X';

  const cells = document.querySelectorAll('.cell');
  const resetButton = document.getElementById('game-reset');
  const leaveButton = document.getElementById('leave-game');

  socket.on('connect', () => {
    socket.emit('join_room_event');
  });

  socket.on('log', (data) => {
    logEvents(data.msg);
  });

  socket.on('move', (data) => {
    cells[data.index].textContent = data.player_marker;
    currentPlayer = data.next_player;
    //logEvents(`${data.player_marker} marked cell ${data.index}`);
    checkGameStatus();
  });

  socket.on('connect_response', (data) => {
    player_marker = data.marker;
    room = data.room;
    username = data.username;
  })

  socket.on('on_win', (data) => {
    logEvent(data.msg)
  })

  socket.on('player_left', (data) => {
    logEvent(data.msg)
    gameActive = false
  })

  cells.forEach(cell => {
    cell.addEventListener('click', () => {
      if (gameActive && cell.textContent.trim() === '') {
        const index = cell.getAttribute('data-cell-index');
        makeMove(index);
      }
    });
  });

  resetButton.addEventListener('click', () => {
    socket.emit('reset', { room });
  });

  leaveButton.addEventListener('click', () => {
    socket.emit('leave', { room });
    window.location.href = "/"; 
  });

  function makeMove(index) {
    if (player_marker === currentPlayer) {
      socket.emit('move', { index, player_marker, room });
    } else {
      logEvent("It's not your turn!");
    }
  }



  function checkGameStatus() {
    if (gameActive === false) return
    const winCombinations = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],
      [0, 3, 6], [1, 4, 7], [2, 5, 8],
      [0, 4, 8], [2, 4, 6]
    ];

    let winner = null;
    winCombinations.forEach(combination => {
      const [a, b, c] = combination;
      if (cells[a].textContent && cells[a].textContent === cells[b].textContent && cells[a].textContent === cells[c].textContent) {
        winner = cells[a].textContent
        console.log(`Winner detected: ${winner}`);
        gameActive = false;
        socket.emit('win', { winner, room });
      }
    });

    if (!winner && Array.from(cells).every(cell => cell.textContent.trim() !== '')) {
      gameActive = false;
      logEvent("It's a draw!");
      socket.emit('draw', { room });
    }
  }
  const logEvents = (msgs) => {
    document.getElementById('game-log-list').innerHTML = '';
    if (msgs === undefined || msgs.length === 0) return
    msgs.forEach((msg) => {
      const p = document.createElement('li');
      p.textContent = msg;
      document.getElementById('game-log-list').appendChild(p);
      document.getElementById('game-log-list').scrollTop = document.getElementById('game-log').scrollHeight;
    })
  }

  const logEvent = (msg) => {
      const p = document.createElement('li');
      p.textContent = msg;
      document.getElementById('game-log-list').appendChild(p);
      document.getElementById('game-log-list').scrollTop = document.getElementById('game-log').scrollHeight;
  }

})

