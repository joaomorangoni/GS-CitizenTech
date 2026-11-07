#include <DHT.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Rede padrao do simulador Wokwi
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// Substitua pelo endereco acessivel do servidor.
const char* API_URL = "";

#define DHT_PIN 4
#define DHT_TYPE DHT22
#define TRIG_PIN 5
#define ECHO_PIN 18

const float DISTANCIA_CRITICA_CM = 10.0;
const float DISTANCIA_ATENCAO_CM = 30.0;
const float UMIDADE_ALTA_PERCENT = 80.0;
const unsigned long INTERVALO_LEITURA_MS = 5000;

DHT dht(DHT_PIN, DHT_TYPE);
unsigned long ultimaLeitura = 0;

void conectarWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando a rede Wokwi-GUEST");

  // Nao bloqueia o monitoramento indefinidamente se a rede estiver indisponivel.
  unsigned long inicio = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - inicio < 15000) {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println(" conectado");
    Serial.print("IP do ESP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(" sem conexao; tentara novamente mais tarde");
  }
}

float medirDistanciaCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long duracao = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duracao == 0) return NAN;
  return duracao * 0.0343f / 2.0f;
}

String classificarRisco(float distanciaCm, float umidade) {
  if (isnan(distanciaCm) || isnan(umidade)) return "DADOS_INVALIDOS";

  // Distancia curta sugere que o fundo/obstrucao esta proximo do sensor.
  // Umidade alta indica ambiente muito umido; o DHT22 nao mede agua parada.
  if (distanciaCm <= DISTANCIA_CRITICA_CM && umidade >= UMIDADE_ALTA_PERCENT)
    return "RISCO_ALTO";
  if (distanciaCm <= DISTANCIA_CRITICA_CM ||
      distanciaCm <= DISTANCIA_ATENCAO_CM ||
      umidade >= UMIDADE_ALTA_PERCENT)
    return "ATENCAO";
  return "SEM_RISCO_DETECTADO";
}

void imprimirLeitura(float distanciaCm, float temperatura, float umidade, const String& risco) {
  Serial.println("\n===== MONITORAMENTO DO BUEIRO =====");
  Serial.print("Distancia sensor-fundo/obstaculo: ");
  if (isnan(distanciaCm)) Serial.println("sem leitura");
  else { Serial.print(distanciaCm, 1); Serial.println(" cm"); }
  Serial.print("Temperatura: ");
  if (isnan(temperatura)) Serial.println("sem leitura");
  else { Serial.print(temperatura, 1); Serial.println(" C"); }
  Serial.print("Umidade relativa do ar: ");
  if (isnan(umidade)) Serial.println("sem leitura");
  else { Serial.print(umidade, 1); Serial.println(" %"); }
  Serial.print("Bueiro: "); Serial.println(risco);
  Serial.println("===================================");
}

void enviarParaServidor(float distanciaCm, float temperatura, float umidade, const String& risco) {
  if (API_URL[0] == '\0') {
    Serial.println("Envio JSON pendente: configure API_URL quando o servidor estiver disponivel.");
    return;
  }
  if (WiFi.status() != WL_CONNECTED) conectarWiFi();
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  if (!http.begin(API_URL)) {
    Serial.println("Nao foi possivel iniciar a requisicao HTTP.");
    return;
  }
  http.addHeader("Content-Type", "application/json");
  String json = "{\"distancia_cm\":";
  if (isnan(distanciaCm)) json += "null"; else json += String(distanciaCm, 1);
  json += ",\"temperatura_c\":";
  if (isnan(temperatura)) json += "null"; else json += String(temperatura, 1);
  json += ",\"umidade_relativa\":";
  if (isnan(umidade)) json += "null"; else json += String(umidade, 1);
  json += ",\"risco\":\"" + risco + "\",\"tempo_ms\":" + String(millis()) + "}";

  int resposta = http.POST(json);
  Serial.print("HTTP: "); Serial.println(resposta);
  if (resposta > 0) Serial.println(http.getString());
  http.end();
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);
  Serial.println("Sistema de monitoramento de bueiro iniciado.");
  conectarWiFi();
}

void loop() {
  if (millis() - ultimaLeitura < INTERVALO_LEITURA_MS && ultimaLeitura != 0) return;
  ultimaLeitura = millis();

  float distancia = medirDistanciaCm();
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();
  String risco = classificarRisco(distancia, umidade);

  imprimirLeitura(distancia, temperatura, umidade, risco);
  enviarParaServidor(distancia, temperatura, umidade, risco);
}

