
import processing.net.*;

// The Server
Server renderServer;
Client client;

// load file
String[] stateFile;

// loaded parameters
int worldSize;
int blockSize;

ArrayList<int[]> snake;
HashMap<String, PImage> images;

int headDirection;
int highScore;
int score;
int[] food;

// application parameters
String[] imagesToLoad = {"head_2", "head_0", "head_3", "head_1", "angle_0", "angle_1", "angle_2", "angle_3", "tail_down", "tail_up", "tail_left", "tail_right", "body_ver", "body_hor", "apple", "heart", "comment", "share"};
int offsetX = 10;
int offsetY = 280;
int recordFrames = 6;

// fonts
PFont bebas;
PFont montserrat;

void setup() {
  
  // init server
  renderServer = new Server(this, 5124);
  
  // load images
  images = new HashMap();
  for (String image: imagesToLoad) {
    images.put(image, loadImage("assets/" + image + ".png"));
  }
  
  // other inits
  bebas = createFont("assets/bebas.ttf", 64);
  montserrat = createFont("assets/montserrat.ttf", 64);
  
  // the size
  size(720,1280);
}

// load state
void loadState() {
  
  // load file
  stateFile = loadStrings("state.txt");
  
  // calculate block size
  worldSize = Integer.parseInt(stateFile[0]);
  blockSize = floor(700 / worldSize);
   
  // get score and parse it to integer
  highScore = Integer.parseInt(stateFile[1]);
  
  // get direction
  headDirection = Integer.parseInt(stateFile[2]);
  
  // get food and parse it to integer
  food = new int[2];
  String[] foody = stateFile[3].split(",");
  food[0] = Integer.parseInt(foody[0]);
  food[1] = Integer.parseInt(foody[1]);
  
  // get snake state and parse integer
  snake = new ArrayList();
  String[] snaky = stateFile[4].split(";");
  for (String s : snaky) {
    String[] ss = s.split(",");
    snake.add(new int[] {Integer.parseInt(ss[0]), Integer.parseInt(ss[1])});
  }
  score = snake.size()-1;
  
}

// score and high score -> top of the screen
void drawScores() {
  fill(0);
  textAlign(CENTER);
  textFont(bebas, 64);
  text("Score " + score, width/2, 140);
  
  fill(80);
  textSize(32);
  text("High Score " + highScore, width/2, 180);
}

// will draw the instructions -> bottom of the screen
void drawInstructions() {
  image(images.get("heart"), 120, 1025, blockSize, blockSize);
  image(images.get("comment"), 320, 1025, blockSize, blockSize);
  image(images.get("share"), 520, 1025, blockSize, blockSize);
  
  text("Forward", 155, 1125);
  text("Left", 355, 1125);
  text("Right", 555, 1125);
  
  textFont(montserrat, 20);
  text("A new video gets posted every 10 minutes, Snake will move according to the top answer!", 50, 1175, 620, 300);
}

// draw outline
void drawOutline() {
  fill(192,249,225);
  stroke(0);
  strokeWeight(3);
  rect(0+offsetX, 0+offsetY, worldSize*blockSize, worldSize*blockSize);
}


// draw food
void drawFood() {
  image(images.get("apple"), food[0]*blockSize+offsetX, food[1]*blockSize+offsetY, blockSize, blockSize);
}


// snake head -> draw based on head direction
void drawSnakeHead(int[] position) {
  image(images.get("head_"+headDirection), position[0]*blockSize+offsetX, position[1]*blockSize+offsetY, blockSize, blockSize);
}


// snake tail -> draw based on previous body position
void drawSnakeTail(int[] position) {
  
  int[] head = snake.get(0);
  int[] prev = snake.get(snake.size()-2);
  String image = null;
  
  // checks for just increased size
  // size of 2
  if (position[0] == head[0] && position[1] == head[1]) {
    return;
  
  // change previous index back by 1
  } else if (position[0] == prev[0] && position[1] == prev[1]) {
    prev = snake.get(snake.size()-3);
  }
  
  // if top
  if (position[1] < prev[1]) {
    image = "tail_up";
    
  // if right
  } else if (position[0] > prev[0]) {
    image = "tail_right";
    
  // if bottom
  } else if (position[1] > prev[1]) {
    image = "tail_down";
    
  // if left
  } else {
    image = "tail_left";
  }
  
  // draw tail
  image(images.get(image), position[0]*blockSize+offsetX, position[1]*blockSize+offsetY, blockSize, blockSize);
}


// draw snake body
void drawSnakeBody(int[] position, int index) {
  
  int[] prev = snake.get(index-1);
  int[] next = snake.get(index+1);
  String image = null;
  
  // just spawned -> so don't draw it
  if (position[0] == next[0] && position[1] == next[1]) return; 
  
  // angle 0
  if ((next[0] > position[0] && prev[1] > position[1]) || (prev[0] > position[0] && next[1] > position[1])) {
    image = "angle_0";
  
  // angle 1
  } else if ((next[0] < position[0] && prev[1] > position[1]) || (prev[0] < position[0] && next[1] > position[1])) {
    image = "angle_1";
  
  // angle 2
  } else if ((next[0] < position[0] && prev[1] < position[1]) || (prev[0] < position[0] && next[1] < position[1])) {
    image = "angle_2";

  // angle 3
  } else if ((next[0] > position[0] && prev[1] < position[1]) || (prev[0] > position[0] && next[1] < position[1])){
    image = "angle_3";
    
  // horizontal
  } else if ((prev[0] < position[0] && position[0] < next[0]) || (prev[0] > position[0] && position[0] > next[0])) {
    image = "body_hor";
   
  // vertical
  } else if ((prev[1] < position[1] && position[1] < next[1]) || (prev[1] > position[1] && position[1] > next[1])) {
    image = "body_ver";
  }
  
  // draw body
  image(images.get(image), position[0]*blockSize+offsetX, position[1]*blockSize+offsetY, blockSize, blockSize);
}


// draw snake
void drawSnake() {
  
  // draw snake
  int i = 0;
  
  for (int[] position : snake) {
    
    // if snake head
    if (i == 0) {
      drawSnakeHead(position);
      
    // draw snake tail
    } else if (snake.size() > 1 && i == snake.size()-1) {
      drawSnakeTail(position);
    
    // draw snake body
    } else {
      drawSnakeBody(position, i);
    }
    
    // keeping track of index
    i++;
  }
}

// record -> returns record state | false = complete, true = ongoing record
void record() {
  
  // save frame and increase frame count
  saveFrame("rendered_images/frame_"+recordFrames+".png");
  
  // increase frame count
  recordFrames+=1;
}

void draw() {
  
  // if recording
  if (recordFrames < 5) {
    
    // debug
    System.out.println("Current Frame: " + recordFrames);
    
    // initial load -> when frame == 0
    if (recordFrames == 0) {
      
      // reload states
      System.out.println("Loaded State");
      loadState();
    }
    
    // clear
    clear();
    background(255);
    
    // draw outline
    drawOutline();
    
    // draw food
    drawFood();
    
    // draw snake
    drawSnake();
    
    // draw score
    drawScores();
    
    // draw instructions
    drawInstructions();
    
    // render images
    record();
    
  } else {
    
    // check if client is connected
    if (client != null) {
      
      // command init to empty
      String command = "";
      
      // Read for client message only if record is completed
      if (recordFrames > 5) {
        command = client.readString();
      }
      
      // if client asked for record
      if (command.equals("record")) {
        
        // debug
        System.out.println("Client initiated record");
        
        // init frames back to 0 -> so that record can be restarted
        recordFrames = 0;
      
      // record is complete
      } else if (recordFrames == 5) {
        
        // tell client that recording is complete
        client.write("complete");
        
        // debug
        System.out.println("Record complete");
        
        // reset client -> cleanup
        client = null;
        recordFrames = 6;
        
      }
      
    } else {
      
      // get client
      client = renderServer.available();
      
      // client connected
      if (client != null) {
        
        // debug
        System.out.println("Client connected!");
      }
      
    }
  
  }
  
}
