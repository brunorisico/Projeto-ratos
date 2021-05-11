#include <Wire.h>
#include <Adafruit_MotorShield.h>

// pins usados para os leds
#define HL_LED_PIN 13
#define LL_LED_PIN 12
#define RL_LED_PIN 11

// pins usados para os receptores do IR Breakbeam Sensors
#define FEEDER_SENSOR_PIN 7
#define LEFT_HOLE_SENSOR_PIN 6
#define RIGHT_HOLE_SENSOR_PIN 5

// sensor states init
int sensorStateFeeder = 1;
int sensorStateLeftHole = 1, previousSensorStateLeftHole = 0;
int sensorStateRightHole = 1, previousSensorStateRightHole = 0;

// timestamp variables
unsigned long arduinoStartedTimestamp = 0;
unsigned long currentItisStartTimestamp = 0;
unsigned long currentDelayStartTimestamp = 0;
unsigned long currentTimeoutStartTimestamp = 0;
unsigned long currentResponseTimeStartTimestamp = 0;
unsigned long currentFeedingTimeStartTimestamp = 0;

// stage flags
bool delayStarted = false; // fica verdadeiro depois do ITIS
bool responseTimeStarted = true;
bool omissionStarted = true;

//trial variables
int currentTrial = 1;
int totalNumberTrials = 100;

// trial timer in milliseconds
unsigned long experimentDuration = 0;

// serial read value
String serialRead = "";

// motor time variables
unsigned long timeDelayFeederSensor = 0;
unsigned long feederDelayMs = 1000;

// variable after delay start (milliseconds)
unsigned long delayStartValue = 3000;

// valores recomendados para a baud rate, quanto mais alto mais rapido, mas nao abusar
// 200, 2400, 4800, 19200, 38400, 57600 e 115200.
#define BAUD_RATE 115200

//motor e shield
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); //instancia do motor shield
// aqui vou buscar o motor que no meu caso esta ligado a porta 2 (m3 e m4)do motor shield
// o motor usado e semelhante ao codigo do exemplo, em que o motor para completar 360 graus
// da 200 steps, o que equivale a 1.8 graus
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2); // AFMS.getStepper(steps_para_360_graus, porta_do_motor);

void(* resetFunc) (void) = 0; // reset arduino

//funcoes para meter o void loop mais limpo
void house_light_on() {
    digitalWrite(HL_LED_PIN, HIGH); 
    Serial.println("HL_ON");
  }

void house_light_off() {
    digitalWrite(HL_LED_PIN, LOW); 
    Serial.println("HL_OFF");
  }

void left_light_on() {
  digitalWrite(LL_LED_PIN, HIGH); 
  Serial.println("LL_ON");
}

void left_light_off() {
  digitalWrite(LL_LED_PIN, LOW); 
  Serial.println("LL_OFF");
 }

void right_light_on() {
  digitalWrite(RL_LED_PIN, HIGH); 
  Serial.println("RL_ON");
}

void right_light_off() {
  digitalWrite(RL_LED_PIN, LOW); 
  Serial.println("RL_OFF");
}

void motor_step_and_detect() {
  // o pellete ao passar tem de quebrar o breaker beam e o sensor ficar low
  // se nao detetar a passagem do pellete enviar mais um mas se falhar novamente
  // parar tudo e avisar que falhou
  myMotor->step(25, FORWARD, SINGLE);
  Serial.println("MO");
  timeDelayFeederSensor = millis();

  while (sensorStateFeeder == 1) {
    sensorStateFeeder = digitalRead(FEEDER_SENSOR_PIN);

    if (sensorStateFeeder == 0) {
      Serial.println("FSA");
      if (digitalRead(sensorStateFeeder == 1)) {
        Serial.println("FSR");
        sensorStateFeeder = 1;
        break;
        }
      }
    else if (millis() > timeDelayFeederSensor + feederDelayMs) {
      if (feederDelayMs == 2000) {
        //failed after 2 seconds stop signal computer and reset arduino
        Serial.println("FSF");
        //ou break;
        delay(1000); //make sure arduino prints the FSF signal before reseting
        resetFunc();
        }
      else {
        myMotor->step(25, FORWARD, SINGLE);
        Serial.println("MO");
      } 
      feederDelayMs = 2000;
    }
  }  
}

bool check_left_sensor_activity() {
  sensorStateLeftHole = digitalRead(LEFT_HOLE_SENSOR_PIN);
  // se rato no sensor --> sensor inter devolve 0 -->  sensor true
  if (!sensorStateLeftHole && previousSensorStateLeftHole) {
    Serial.println("LSA");
    previousSensorStateLeftHole = sensorStateLeftHole; 
    return true;
   }
  if (sensorStateLeftHole && !previousSensorStateLeftHole) {
    Serial.println("LSR");
    previousSensorStateLeftHole = sensorStateLeftHole; 
    return false;
  } 
}

bool check_right_sensor_activity() {
  sensorStateRightHole = digitalRead(RIGHT_HOLE_SENSOR_PIN);
  if (!sensorStateRightHole && previousSensorStateRightHole) {
    Serial.println("RSA");
    previousSensorStateRightHole = sensorStateRightHole; 
    return true;
  }
  if (sensorStateRightHole && !previousSensorStateRightHole) {
    Serial.println("RSR");
    previousSensorStateRightHole = sensorStateRightHole; 
    return false;
  }  
}

void TO_start() {
  //TO_start em loop de 3 segundos ate o sensor nao detetar nada
  currentTimeoutStartTimestamp = millis();
  Serial.println("TO");
  while ( millis() < currentTimeoutStartTimestamp + 3000) {
    check_left_sensor_activity(); //ve se o rato vai ao sensor da esquerda mas nao faz nada para alem de registar o evento
    while (check_right_sensor_activity() == 0){
      // fica preso aqui ate o rato sair do sensor da direita
      // se saltar fora aguarda 3 segundos para ver se nao vai para la outra vez
      currentTimeoutStartTimestamp = millis();      
    }
  } 
}

void ITI_start(){
  currentItisStartTimestamp = millis();
  Serial.println("ITIS");
  while ( millis() < currentItisStartTimestamp + 3000) {
    check_right_sensor_activity(); //ve se o rato vai ao sensor da direita mas nao faz nada para alem de registar o evento
    while (check_left_sensor_activity() == 0){
      // fica preso aqui ate o rato sair do sensor da esquerda
      // se saltar fora aguarda 3 segundos para ver se nao vai para la outra vez
      currentItisStartTimestamp = millis(); 
    }
         
  }
}

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(1);

  randomSeed(analogRead(0)); //making the random generator for the 6 or 12 is more random...

  AFMS.begin();
  myMotor->setSpeed(255);  // 255 rpm maxima velocidade

    // configurar os pins dos leds para OUTPUT
  pinMode(HL_LED_PIN, OUTPUT);
  pinMode(LL_LED_PIN, OUTPUT);
  pinMode(RL_LED_PIN, OUTPUT);

  // configurar os sensores
  pinMode(FEEDER_SENSOR_PIN, INPUT);
  pinMode(LEFT_HOLE_SENSOR_PIN, INPUT);
  pinMode(RIGHT_HOLE_SENSOR_PIN, INPUT);

  digitalWrite(FEEDER_SENSOR_PIN, HIGH);
  digitalWrite(LEFT_HOLE_SENSOR_PIN, HIGH);
  digitalWrite(RIGHT_HOLE_SENSOR_PIN, HIGH);

}

void loop() {
  // pre-trial
  serialRead = Serial.readString();
  if (serialRead == "train" or serialRead == "test") {
    delay(100);
    arduinoStartedTimestamp = millis();
    Serial.println("SA");

    //fazer um quick check aos sensores...
    check_left_sensor_activity();
    check_right_sensor_activity();

    house_light_on();
    //motor_step_and_detect();
    left_light_on();

    while (millis() < arduinoStartedTimestamp + 5000) {
      // 5 segundos para recolher???
      if (check_left_sensor_activity() == 0) {
        break;
        }     
    }
    left_light_off();
    ITI_start();
    Serial.println("ART");
    
    delayStarted = true;
    if (serialRead == "train") {
      experimentRunning = "train";
      totalNumberTrials = 100;
      experimentDuration = 1800000; // 30 min
      } else {
        experimentRunning = "test";
        totalNumberTrials = 120;
        experimentDuration = 3600000; // 60 min
        }
    serialRead = ""; 
  }
   
  //aqui inicia o Delay start
  else if (delayStarted and (currentTrial <= totalNumberTrials) and (millis() - arduinoStartedTimestamp < experimentDuration)) {
    currentDelayStartTimestamp = millis();
    Serial.println("DS");

    //meter isto como true pois podem se tornar false mais a frente consoante as respostas do rato e por isto estar em loop
    responseTimeStarted = true;   
    omissionStarted = true;  
    
    // intervalo de 3 segundos depois do Delay start
    // se sensor direita (RS) ativado, Premature Response
    // como nao ha castigo por premature response no test meter aqui uma flag
    // e criar tambem uma variavel que pode ser 6 ou 12s entre os 25 a 95 trials
    if (experimentRunning == "test" and  95 > currentTrial >= 70) {
      delayStartValue = random(0, 2);
      if (delayStartValue == 0) {
        delayStartValue = 6000;
        } else {delayStartValue = 12000;}
    } else {delayStartValue = 3000;}

    while (millis() < currentDelayStartTimestamp + delayStartValue) {
      check_left_sensor_activity(); //ve se o rato vai ao sensor da esquerda mas nao faz nada para alem de registar o evento   
      if (check_right_sensor_activity() == 0){     
        //castigo com a luz desligado se train e fim do trial
        // senao so ve tambem se ha atividade no sensor da direita
        if (experimentRunning == "train") {
          house_light_off();  
          Serial.println("PR");
          
          //como ha PR nao vamos para as fases seguintes e isto volta para o delay start apos o TO_start acabar
          responseTimeStarted = false;
          
          //TO_start em loop de 3 segundos ate o sensor nao detetar nada
          TO_start();
          //voltar a ligar a luz apos acabar castigo
          house_light_on();
          Serial.println("TE");
          currentTrial = currentTrial + 1;
       } else if (experimentRunning == "test"){
          Serial.println("PR");
          while (check_right_sensor_activity() == 0){} // se o rato fica no sensor da direita a experiencia nao avanca!!!! Pode ser um problema???  
        }
     }
    }
    // se o sensor nao foi ativado anterioremente...
    if (responseTimeStarted) { 
      currentResponseTimeStartTimestamp = millis();
      Serial.println("RTS");
      right_light_on();

      // intervalo de 60 segundos
      while(millis() < currentResponseTimeStartTimestamp + 60000) {
        check_left_sensor_activity(); //ve se o rato vai ao sensor da esquerda mas nao faz nada para alem de registar o evento
        if (check_right_sensor_activity() == 0) {
          //como ativou esta resposta ja nao vai para o omission response
          Serial.println("TR");
          omissionStarted = false;   
            
          while (check_right_sensor_activity() == 0){} // espera para que o sensor right (3) seja inativado
          right_light_off();
          //motor_step_and_detect();
          left_light_on();

          // feeding time start
          currentFeedingTimeStartTimestamp = millis();
          Serial.println("FTS");
          while(millis() < currentFeedingTimeStartTimestamp + 30000) {
            if (check_right_sensor_activity() == 0) {
              //Perseverant response
              Serial.println("SR");
              while (check_right_sensor_activity() == 0){} // espera para que o sensor right (3) seja inativado
              
              // restart do tempo do FTS????
              currentFeedingTimeStartTimestamp = millis();
              Serial.println("FTS");
            }
            else if (check_left_sensor_activity() == 0) {
              while (check_left_sensor_activity() == 0){} // espera para que o sensor left (3) seja inativado
              // break the FDS 30s interval loop
              break;
            }
          }
          left_light_off();
          Serial.println("TE");
          currentTrial = currentTrial + 1;
          ITI_start();
          
          break; //get out of the 60 second loop
        }
      }
      //se enao aconteceu nada nos 60 segundos vem para aqui
      if (omissionStarted) {
        Serial.println("OR");
        right_light_off();
        house_light_off(); 
        
        //TO_start em loop de 3 segundos ate o sensor nao detetar nada
        TO_start();
        house_light_on();
        Serial.println("TE");
        currentTrial = currentTrial + 1;
      }    
    }
  }
    //como o Arduino funciona em loop isto volta para o delay start se o delayStarted for true
}

  
