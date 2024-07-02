#include <PID_v1.h>
#include <Arduino.h>

// Define the PID controller's input, output, and setpoint variables
double Setpoint, Input, Output;
// Define the PID controller's tuning parameters
double Kp=2, Ki=1, Kd=1;

// Create the PID controller
PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);



float Dutycycle = 0.00;
float Voltage_output = 4.6;
float voltage_input = 0.00;
double current_output = 0.00;
double current_input = 0.00;
int potentiometer = A0;
int mosfet = 11;
int voltage_output_pin = A1;  // Define the pin for voltage output
int voltage_input_pin = A2;  // Define the pin for voltage input
int current_output_pin = A5;  // Define the pin for current output
int current_input_pin = A4;  // Define the pin for current input
int samples_no = 0;

float SamplesO=0.0,SamplesI=0.0;
double AvgAcsO =0.00,AcsValueO=0.00, AvgAcsI = 0.00, AcsValueI = 0.00;


unsigned long previousMillis = 0;  // will store the last time the code was executed
const long interval = 250;  // interval at which to execute code (milliseconds)


void setup() {
  Serial.begin(9600); // Initialize serial communication
  pinMode(potentiometer, INPUT);
  pinMode(mosfet, OUTPUT);
  pinMode(voltage_output_pin, INPUT);  // Set the voltage output pin as input
  pinMode(voltage_input_pin, INPUT);  // Set the voltage input pin as input
  pinMode(current_output_pin, INPUT);  // Set the current output pin as input
  pinMode(current_input_pin, INPUT);  // Set the current input pin as input
  TCCR2B = TCCR2B & B11111000 | B00000001; // Set PWM frequency for D3 & D11 to 31372.55 Hz
  myPID.SetOutputLimits(0, 127);
  // Turn the PID controller on
  myPID.SetMode(AUTOMATIC);
  //myPID.SetControllerDirection(REVERSE);  // Reverse the direction of the controller
  Setpoint = 8.0;

}

void loop() {



float PWM_value = map(analogRead(potentiometer), 0, 1024, 0, 255);
//analogWrite(mosfet, PWM_value);
Dutycycle = map(PWM_value,0,255,0,100);


float voltage_output_read = analogRead(voltage_output_pin) * (5.0 / 1023.0);  // Convert the analog read value to voltage
Voltage_output = floatMap(voltage_output_read, 0.0, 5.0, 0.0, 92.15);  // Map the voltage output
Input = Voltage_output;

float voltage_input_read = analogRead(voltage_input_pin) * (5.0 / 1023.0);  // Convert the analog read value to voltage
voltage_input = floatMap(voltage_input_read, 0.0, 5.0, 0.0, 33.35);  // Map the voltage input

//float current_output_read = analogRead(current_output_pin) * (-5.0 / 1023.0);  // Convert the analog read value to voltage
//current_output = (2.44 - (current_output_read) )/0.066; // Map the current output
//current_output = analogRead(current_output_pin);

  // Compute the PID controller's output
  myPID.Compute();
  analogWrite(mosfet, round(Output));
  //analogWrite(mosfet, PWM_value);

              AcsValueO = analogRead(A5);     //Read current sensor values   
              AcsValueI = analogRead(A4);     //Read current sensor values
              SamplesO = SamplesO + AcsValueO;  //Add samples together
              SamplesI = SamplesI + AcsValueI;  //Add samples together
              samples_no++;



unsigned long currentMillis = millis();
 if (currentMillis - previousMillis >= interval) 
  {          /*unsigned int x=0;
            float SamplesO=0.0,SamplesI=0.0;
            double AvgAcsO =0.00,AcsValueO=0.00, AvgAcsI = 0.00, AcsValueI = 0.00;

              for (int x = 0; x < 150; x++){ //Get 150 samples
              AcsValueO = analogRead(A5);     //Read current sensor values   
              AcsValueI = analogRead(A4);     //Read current sensor values
              SamplesO = SamplesO + AcsValueO;  //Add samples together
              SamplesI = SamplesI + AcsValueI;  //Add samples together
              delay (3); // let ADC settle before next sample 3ms
            }*/
          AvgAcsO=SamplesO/samples_no;//Taking Average of SamplesO
          AvgAcsI=SamplesI/samples_no;//Taking Average of SamplesI
          SamplesO=0.0;//Clearing SamplesO
          SamplesI=0.0;//Clearing SamplesI
          samples_no=0;//Clearing samples_no

          AcsValueO = (2.52 - (AvgAcsO * (5.0 / 1024.0)) )/0.000185;
          AcsValueI = (2.52 - (AvgAcsI * (5.0 / 1024.0)) )/-0.000185;
          
          //current_input = (2.52 - (AvgAcsO * (5.0 / 1024.0)));
          //current_input = floatMap(current_input, 0.00, 1.00, 0.00, 0.185);

              current_output = AcsValueO;//Print the read current on Serial monitor
              current_input = AcsValueI;

    previousMillis = currentMillis;
    Serial.print("data"); Serial.print(",");
    Serial.print(floatMap(Output,0,127,0,49.8)); Serial.print(",");
    //Serial.print(Dutycycle); Serial.print(",");
    Serial.print(Voltage_output); Serial.print(",");
    Serial.print(voltage_input); Serial.print(",");
    Serial.print(current_output); Serial.print(",");
    Serial.print(current_input); Serial.print(",");
    Serial.print(Setpoint); Serial.print(",");
    Serial.print(Kp); Serial.print(",");
    Serial.print(Ki); Serial.print(",");
    Serial.println(Kd);
 }

  if (Serial.available()) {
    double V1, V2, V3, V4;
    // Read the serial input until a newline character is encountered
    String input = Serial.readStringUntil('\n');
    // Parse the serial input
        char* str = strdup(input.c_str());  // Create a mutable C-string copy of input

        char* token = strtok(str, ",");
        if (token != NULL) {
            V1 = atof(token);
            token = strtok(NULL, ",");
        }

        if (token != NULL) {
            V2 = atof(token);
            token = strtok(NULL, ",");
        }

        if (token != NULL) {
            V3 = atof(token);
            token = strtok(NULL, ",");
        }

        if (token != NULL) {
            V4 = atof(token);
        }

        free(str);  // Free the allocated memory
    Setpoint = V1;
    Kp = V2;
    Ki = V3;
    Kd = V4;
    // Update the PID controller's tuning parameters
    myPID.SetTunings(Kp, Ki, Kd);
    delay(100);
    Serial.print("flag"); Serial.print(","); 
    Serial.print(Setpoint); Serial.print(",");
    Serial.print(Kp); Serial.print(",");
    Serial.print(Ki); Serial.print(",");
    Serial.println(Kd); 
  }

delay(10);
}




float floatMap(double x, double in_min, double in_max, double out_min, double out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}
