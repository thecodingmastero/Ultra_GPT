// Basic canvas setup and game state
const canvas = document.getElementById("game-canvas");
const ctx = canvas.getContext("2d");

const WIDTH = canvas.width;
const HEIGHT = canvas.height;

// Game variables
let gameRunning = false;
let score = 0;
let player = { x: 50, y: HEIGHT - 80, width: 50, height: 50, vy: 0, onGround: false };
let keys = {};
let gravity = 0.8;
let platforms = [];
let enemies = [];
let quizActive = false;
let investmentBalance = 1000;
let stocksOwned = {};

const quizQuestions = [
  {
    question: "What does 'dividend' mean?",
    options: ["Company profit share", "Stock price", "Bond interest", "Stock split"],
    answer: 0,
  },
  {
    question: "What is a 'bull market'?",
    options: ["Falling prices", "Rising prices", "Stable prices", "No stocks available"],
    answer: 1,
  },
  // Add more questions...
];

// Initialize platforms
function createPlatforms() {
  platforms = [
    { x: 0, y: HEIGHT - 30, width: WIDTH, height: 30 },
    { x: 150, y: HEIGHT - 120, width: 120, height: 20 },
    { x: 350, y: HEIGHT - 200, width: 140, height: 20 },
    { x: 600, y: HEIGHT - 150, width: 120, height: 20 },
  ];
}

// Initialize enemies
function createEnemies() {
  enemies = [
    { x: 200, y: HEIGHT - 150, width: 40, height: 40, direction: 1, speed: 2 },
    { x: 500, y: HEIGHT - 190, width: 40, height: 40, direction: -1, speed: 1.5 },
  ];
}

// Draw player
function drawPlayer() {
  ctx.fillStyle = "#3e9fcd";
  ctx.fillRect(player.x, player.y, player.width, player.height);
}

// Draw platforms
function drawPlatforms() {
  ctx.fillStyle = "#428ce2";
  platforms.forEach((p) => {
    ctx.fillRect(p.x, p.y, p.width, p.height);
  });
}

// Draw enemies
function drawEnemies() {
  ctx.fillStyle = "#c0f0f7";
  enemies.forEach((e) => {
    ctx.fillRect(e.x, e.y, e.width, e.height);
  });
}

// Player movement and physics
function updatePlayer() {
  if (keys["ArrowLeft"]) player.x -= 5;
  if (keys["ArrowRight"]) player.x += 5;

  player.vy += gravity;
  player.y += player.vy;

  player.onGround = false;

  platforms.forEach((p) => {
    if (
      player.x < p.x + p.width &&
      player.x + player.width > p.x &&
      player.y + player.height > p.y &&
      player.y + player.height < p.y + p.height
    ) {
      player.y = p.y - player.height;
      player.vy = 0;
      player.onGround = true;
    }
  });

  // Boundaries
  if (player.x < 0) player.x = 0;
  if (player.x + player.width > WIDTH) player.x = WIDTH - player.width;
  if (player.y > HEIGHT) {
    gameOver("You fell off!");
  }
}

// Enemy movement
function updateEnemies() {
  enemies.forEach((e) => {
    e.x += e.speed * e.direction;
    if (e.x < 0 || e.x + e.width > WIDTH) {
      e.direction *= -1;
    }

    // Collision with player
    if (
      player.x < e.x + e.width &&
      player.x + player.width > e.x &&
      player.y < e.y + e.height &&
      player.y + player.height > e.y
    ) {
      gameOver("You hit an enemy!");
    }
  });
}

// Jump function
function jump() {
  if (player.onGround) {
    player.vy = -15;
    player.onGround = false;
  }
}

// Game over
function gameOver(msg) {
  alert(msg + " Game over!");
  resetGame();
}

// Reset game
function resetGame() {
  score = 0;
  investmentBalance = 1000;
  stocksOwned = {};
  player.x = 50;
  player.y = HEIGHT - 80;
  player.vy = 0;
  createPlatforms();
  createEnemies();
  updateScore();
  gameRunning = false;
  quizActive = false;
}

// Update score display
function updateScore() {
  document.getElementById("score-display").textContent = "Score: " + score;
  updateInvestmentPanel();
}

// Quiz popup function (simple prompt-based quiz)
function showQuiz() {
  quizActive = true;
  const q = quizQuestions[Math.floor(Math.random() * quizQuestions.length)];
  let optionsText = q.options.map((o, i) => `${i + 1}: ${o}`).join("\n");
  let answer = prompt(`${q.question}\n${optionsText}\n\nEnter the number of your answer:`);

  if (answer === null) {
    // User canceled the quiz
    quizActive = false;
    return;
  }

  let answerNum = parseInt(answer.trim());
  if (answerNum === q.answer + 1) {
    alert("Correct! You earned 100 points.");
    score += 100;
  } else {
    alert(`Wrong! The correct answer was: ${q.options[q.answer]}`);
    score -= 50;
  }
  updateScore();
  quizActive = false;
}

// Investment panel update
function updateInvestmentPanel() {
  const panel = document.getElementById("investment-panel");
  panel.innerHTML = `
    <p>Balance: $${investmentBalance.toFixed(2)}</p>
    <p>Stocks Owned: ${Object.keys(stocksOwned).length || 0}</p>
    <button id="buy-stock-btn">Buy Random Stock ($100)</button>
    <button id="sell-stock-btn">Sell All Stocks</button>
  `;

  document.getElementById("buy-stock-btn").onclick = async () => {
    if (investmentBalance < 100) {
      alert("Not enough balance!");
      return;
    }
    // Buy a random stock symbol from a list
    const symbols = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN"];
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];

    try {
      const res = await fetch(`/price?symbol=${symbol}`);
      const data = await res.json();

      if (data.price) {
        stocksOwned[symbol] = (stocksOwned[symbol] || 0) + 1;
        investmentBalance -= 100;
        alert(`Bought 1 share of ${symbol} at $${data.price}`);
        updateScore();
      } else {
        alert("Could not fetch price to buy.");
      }
    } catch {
      alert("Network error while buying stock.");
    }
  };

  document.getElementById("sell-stock-btn").onclick = () => {
    if (Object.keys(stocksOwned).length === 0) {
      alert("You don't own any stocks!");
      return;
    }
    let earnings = 0;
    for (const symbol in stocksOwned) {
      const qty = stocksOwned[symbol];
      // For simplicity, assume sell price = $110 per stock
      earnings += qty * 110;
    }
    alert(`Sold all stocks for $${earnings.toFixed(2)}!`);
    investmentBalance += earnings;
    stocksOwned = {};
    updateScore();
  };
}

// Game loop
function gameLoop() {
  if (!gameRunning) return;
  ctx.clearRect(0, 0, WIDTH, HEIGHT);

  drawPlatforms();
  drawEnemies();
  drawPlayer();

  updatePlayer();
  updateEnemies();

  // Random chance to trigger quiz
  if (!quizActive && Math.random() < 0.001) {
    showQuiz();
  }

  // Increase score slowly
  score += 0.1;
  updateScore();

  requestAnimationFrame(gameLoop);
}

// Input handlers
window.addEventListener("keydown", (e) => {
  keys[e.key] = true;
  if (e.key === " " || e.key === "ArrowUp") {
    jump();
  }
});
window.addEventListener("keyup", (e) => {
  keys[e.key] = false;
});

// Buttons
document.getElementById("start-game").onclick = () => {
  if (!gameRunning) {
    gameRunning = true;
    gameLoop();
  }
};

document.getElementById("reset-game").onclick = () => {
  resetGame();
};

// Initialize on page load
resetGame();
