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
int sensorStateFeeder = HIGH;
int sensorStateLeftHole = HIGH;
int previousSensorStateLeftHole = HIGH;
int sensorStateRightHole = HIGH;
int previousSensorStateRightHole = HIGH;

// variables
int arduinoStartedTimestamp = 0;
int currentItisStartTimestamp = 0;
int currentDelayStartTimestamp = 0;
int currentTimeoutStartTimestamp = 0;
int currentResponseTimeStartTimestamp = 0;
int currentFeedingTimeStartTimestamp = 0;

// stage flags
bool delayStarted = false; // fica verdadeiro depois do ITIS
bool responseTimeStarted = true;
bool omissionStarted = true;

// motor time variables
int timeDelayFeederSensor = 0;
int feederDelayMs = 1000;

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
     
  while (sensorStateFeeder == HIGH) {
    //sensorStateFeeder = digitalRead(FEEDER_SENSOR_PIN);
    sensorStateFeeder  = LOW; //APAGAR ISTO DEPOIS, SO PARA TESTES!!!!
    if (sensorStateFeeder == LOW) {
      Serial.println("FSA");
      if (digitalRead(FEEDER_SENSOR_PIN == HIGH)) {
        Serial.println("FSR");
        }
      }
    else if (millis() > timeDelayFeederSensor + feederDelayMs) {
      if (feederDelayMs == 2000) {
        //failed after 2 seconds stop signal computer and reset arduino
        Serial.println("FSF");
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
  if (previousSensorStateLeftHole != sensorStateLeftHole) {
    if (sensorStateLeftHole == LOW) {
      Serial.println("LSA");
      previousSensorStateLeftHole = sensorStateLeftHole; 
      return true;
     }
    else if (sensorStateLeftHole == HIGH) {
      Serial.println("LSR");
      previousSensorStateLeftHole = sensorStateLeftHole; 
      return false;
    }  
  }
  return previousSensorStateLeftHole;  
}

bool check_right_sensor_activity() {
  sensorStateRightHole = digitalRead(RIGHT_HOLE_SENSOR_PIN);
  if (previousSensorStateRightHole != sensorStateRightHole) {
    if (sensorStateRightHole == LOW) {
      Serial.println("RSA");
      previousSensorStateRightHole = sensorStateRightHole; 
      return true;
    }
    else if (sensorStateRightHole == HIGH) {
      Serial.println("RSR");
      previousSensorStateRightHole = sensorStateRightHole; 
      return false;
    }  
  } 
  return previousSensorStateRightHole;
}

void TO_start() {
  //TO_start em loop de 3 segundos ate o sensor nao detetar nada
  currentTimeoutStartTimestamp = millis();
  while ( millis() < currentTimeoutStartTimestamp + 3000) {
    Serial.println("TO");
    check_left_sensor_activity(); //ve se o rato vai ao sensor da esquerda mas nao faz nada para alem de registar o evento
    while (check_right_sensor_activity()){
      // fica preso aqui ate o rato sair do sensor da direita
      // se saltar fora aguarda 3 segundos para ver se nao vai para la outra vez
      currentTimeoutStartTimestamp = millis();      
    }
  } 
}


void setup() {
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(1);

  AFMS.begin();
  myMotor->setSpeed(255);  // 255 rpm maxima velocidade
}

void loop() {
  // pre-trial  
  if (Serial.readString() == "start") {
    arduinoStartedTimestamp = millis();
    Serial.println("SA");
    
    house_light_on();
    motor_step_and_detect();
    left_light_on();

    while (millis() < arduinoStartedTimestamp + 5000) {
      // 5 segundos para recolher???
      check_left_sensor_activity();
    }
    left_light_off();

    currentItisStartTimestamp = millis();
    while ( millis() < currentItisStartTimestamp + 3000) {
      Serial.println('ITIS');
      check_right_sensor_activity(); //ve se o rato vai ao sensor da direita mas nao faz nada para alem de registar o evento
      while (check_left_sensor_activity()){
        // fica preso aqui ate o rato sair do sensor da esquerda
        // se saltar fora aguarda 3 segundos para ver se nao vai para la outra vez
        currentItisStartTimestamp = millis();      
      }
    }
    delayStarted = true;
  }
  //aqui inicia o Delay start
  else if (delayStarted) {
    currentDelayStartTimestamp = millis();
    Serial.println('DS');

    //meter isto como true pois podem se tornar false mais a frente consoante as respostas do rato e por isto estar em loop
    responseTimeStarted = true;   
    omissionStarted = true;  
    
    // intervalo de 3 segundos depois do Delay start
    // se sensor direita (RS) ativado, Premature Response
    while (millis() < currentDelayStartTimestamp + 3000) {
      check_left_sensor_activity(); //ve se o rato vai ao sensor da esquerda mas nao faz nada para alem de registar o evento
      if (check_right_sensor_activity()){
        //castigo com a luz desligado
        house_light_off();  
        Serial.println('PR');
        
        //como ha PR nao vamos para as fases seguintes e isto volta para o delay start apos o TO_start acabar
        responseTimeStarted = false;
        
        //TO_start em loop de 3 segundos ate o sensor nao detetar nada
        TO_start();
        //voltar a ligar a luz apos acabar castigo
        house_light_on();  
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
        if (check_right_sensor_activity()) {
          //como ativou esta resposta ja nao vai para o omission response
          omissionStarted = false;   
             
          while (check_right_sensor_activity()){} // espera para que o sensor right (3) seja inativado
          right_light_off();
          motor_step_and_detect();
          left_light_on();

          // feeding time start
          currentFeedingTimeStartTimestamp = millis();
          Serial.println("FTS");
          while(millis() < currentResponseTimeStartTimestamp + 30000) {
            if (check_right_sensor_activity()) {
              //Perseverant response
              Serial.println("SR");
              while (check_right_sensor_activity()){} // espera para que o sensor right (3) seja inativado
              
              // restart do tempo do FTS????
              currentFeedingTimeStartTimestamp = millis();
              Serial.println("FTS");
            }
            else if (check_left_sensor_activity()) {
              while (check_left_sensor_activity()){} // espera para que o sensor left (3) seja inativado
              // break the FDS 30s interval loop
              break;
            }
          }
          // if no sensor activated...
          left_light_off();
          
          break; //get out of the 60 second loop
        }
      }
      //se enao aconteceu nada nos 60 segundos vem para aqui
      if (omissionStarted) {
        right_light_off();
        house_light_off(); 
        
        //TO_start em loop de 3 segundos ate o sensor nao detetar nada
        TO_start();
        house_light_on();
      }    
    }
    //como o Arduino funciona em loop isto volta para o delay start se o delayStarted for true
  }  
}

  
