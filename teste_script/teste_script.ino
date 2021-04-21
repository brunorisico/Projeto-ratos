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
int sensorStateRightHole = HIGH;

// variables
int arduino_started_timestamp = 0;

// motor time variables
int time_delay_feeder_sensor = 0;
int feeder_delay_ms = 1000;

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
    time_delay_feeder_sensor = millis();
       
    while (sensorStateFeeder == HIGH) {
      //sensorStateFeeder = digitalRead(FEEDER_SENSOR_PIN);
      sensorStateFeeder  = LOW; //APAGAR ISTO DEPOIS, SO PARA TESTES!!!!
      if (sensorStateFeeder == LOW) {
        Serial.println("FSA");
        }
      else if (millis() > time_delay_feeder_sensor + feeder_delay_ms) {
        if (feeder_delay_ms == 2000) {
          //failed after 2 seconds stop signal computer and reset arduino
          Serial.println("FSF");
          delay(1000); //make sure arduino prints the FSF signal before reseting
          resetFunc();
          }
        else {
          myMotor->step(25, FORWARD, SINGLE);
          Serial.println("MO");
        } 
        feeder_delay_ms = 2000;
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
    arduino_started_timestamp = millis();
    Serial.println("SA");
    
    house_light_on();
    motor_step_and_detect();
    left_light_on();

    while (millis() < arduino_started_timestamp + 5000) {
      sensorStateLeftHole = digitalRead(LEFT_HOLE_SENSOR_PIN);
      

      
      } 
    }
 

//Serial.println("LL_ON");
//Serial.println("LL_OFF");

//    
//    Serial.println("MO");
//    Serial.println("LL_ON");
//    delay(5000);
//    Serial.println("LL_OFF");
//    
//    delay(3000);    
}

  
