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
int sensorStateFeeder = 0;
int sensorStateLeftHole = 0;
int sensorStateRightHole = 0;

int feeder_backup_threshold = 0;

// valores recomendados para a baud rate, quanto mais alto mais rapido, mas nao abusar
// 200, 2400, 4800, 19200, 38400, 57600 e 115200.
#define BAUD_RATE 115200

bool python_start = true; //boolean para teste, a ser trocado no futuro pelo flag dado pela interface em python

//motor e shield
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); //instancia do motor shield
// aqui vou buscar o motor que no meu caso esta ligado a porta 2 (m3 e m4)do motor shield
// o motor usado e semelhante ao codigo do exemplo, em que o motor para completar 360 graus
// da 200 steps, o que equivale a 1.8 graus
Adafruit_StepperMotor *myMotor = AFMS.getStepper(200, 2); // AFMS.getStepper(steps_para_360_graus, porta_do_motor);

void(* resetFunc) (void) = 0; // reset arduino

void setup() {
  // iniciar o serial para poder comunicar com a interface feita em Python
  Serial.begin(BAUD_RATE);

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

}

void loop() {
  if (python_start == true) {
    Serial.println("A iniciar o loop");
    
    //Antes do ITI start
    //Ligar a luz da caixa  
    digitalWrite(HL_LED_PIN, HIGH);
    
    //dispensar um pellete
    //step 25 equivale a 45 graus ja que temos 8 buracos para dispensar comida...
    myMotor->step(25, FORWARD, SINGLE); 
    Serial.println("Pellet teoricamente dispensado");
    
    // o pellete ao passar tem de quebrar o breaker beam e o sensor ficar low
    do {
      sensorStateFeeder = digitalRead(FEEDER_SENSOR_PIN);
      if (sensorStateFeeder == LOW) {
          Serial.println("Detetada a passagem do pellet");
        } else {
          delay(1);
          feeder_backup_threshold = feeder_backup_threshold + 1;
          if(feeder_backup_threshold == 1000) {
            myMotor->step(25, FORWARD, SINGLE);
            Serial.println("Mais um pellet..."); 
            } else if (feeder_backup_threshold == 1001) {
              resetFunc();
              }
        }
    } while (sensorStateFeeder != LOW);
    
    
    delay(50000);
    
    digitalWrite(LL_LED_PIN, HIGH);
  }
}
