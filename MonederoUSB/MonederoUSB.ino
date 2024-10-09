
const int coinpin = 2;//pin al cual estara conectada la señal del monedero
const int ledpin = 13;//pin al cual estara conectado un led, para indicar cuando una moneda es aceptada.
volatile int pulse= 0; //Contador de monedas/pulsos insertadas.
boolean bInserted = false; //Variable de control para identificar cuando una moneda es insertada.

void setup() {
  // Inicializamos el puerto serial.
  Serial.begin(9600);

  //Agregamos la interrupcion con el pin indicado.
  attachInterrupt(digitalPinToInterrupt(coinpin), coinInterrupt, RISING);

  //Asignamos el pin para el led como salida
  pinMode(ledpin, OUTPUT);
  
}

void loop() {
   
  if( bInserted  ){ // Validamos si hay una moneda insertada.
     bInserted = false; //Apagamos la variable de control
     digitalWrite(ledpin, HIGH); //Encendemos el led
     Serial.println("COIN"); //Imprimimos en el puerto serial la palabra "COIN"   
     delay(1000); //Esperamos un segundo.
  }else{
  // Apagamos el led.
  digitalWrite(ledpin, LOW);
  }
  
}

// Interrupcion.
void coinInterrupt(){
 
  // Cada vez que insertamos una moneda valida, incrementamos el contador de monedas y encendemos la variable de control,
  pulse++ ;
  bInserted = true;
   
}
