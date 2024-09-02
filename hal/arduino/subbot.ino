#include <Servo.h>
#include <Arduino_JSON.h>
#include <Arduino_AVRSTL.h>
#include <assert.h>
#include <map>
#include <String>

constexpr short svo_num = 2;
constexpr short svo_dig_pin[svo_num] = {9, 10};
Servo svo[svo_num]; // al, ar, tl, tr
short svo_angle[svo_num];
std::map<String, short> svo_name2idx = {{"al", 0}, {"ar", 1}};

constexpr short eng_num = 1;
constexpr short eng_dig_pin[eng_num] = {11};
Servo eng[eng_num]; // al, ar, tl, tr
short eng_speed[eng_num];
std::map<String, short> eng_name2idx = {{"e1", 0}};
JSONVar data;

void svo_set(short idx, short angle){
    svo[idx].write(angle);
    svo_angle[idx] = angle;
    delay(15);
}

short svo_get(short idx){
    return svo_angle[idx];
}

void svo_pnt_by_name(String name){
    Serial.print("{\"" + name + "\":");
    Serial.print(svo_angle[svo_name2idx[name]]);
    Serial.print("}\r\n");
}

void svo_set_by_name(String name, short num){
    svo_set(svo_name2idx[name], num);
}

void eng_set(short idx, short speed){
    eng[idx].writeMicroseconds(speed);
    eng_speed[idx] = speed;
    delay(15);
}

short eng_get(short idx){
    return eng_speed[idx];
}

void eng_pnt_by_name(String name){
    Serial.print("{\"" + name + "\":");
    Serial.print(eng_speed[eng_name2idx[name]]);
    Serial.print("}\r\n");
}

void eng_set_by_name(String name, short num){
    eng_set(eng_name2idx[name], num);
}

void setup() {
    for(short i = 0; i < svo_num; ++i){
        svo[i].attach(svo_dig_pin[i]);
    }
    for(short i = 0; i < svo_num; ++i){
        svo_set(i, 0);
    }
    for(short i = 0; i < eng_num; ++i){
        eng[i].attach(eng_dig_pin[i]);
    }
    for(short i = 0; i < eng_num; ++i){
        eng_set(i, 0);
    }
    Serial.begin(9600);
    //Serial.println("\r\n");
}
void handle(String type, String device, String option, short num){
    if(type == "svo"){
        if(option == "q"){
            svo_pnt_by_name(device);
        }
        if(option == "s"){
            svo_set_by_name(device, num);
        }
    }
    if(type == "eng"){
        if(option == "q"){
            eng_pnt_by_name(device);
        }
        if(option == "s"){
            eng_set_by_name(device, num);
        }
    }
}

void loop() {
    //Serial.print("hihihi\r\n");
    //Serial.print("\r\n");
    while(Serial.available() == 0);
    data = JSON.parse(Serial.readString());
    if(JSON.typeof(data) == "undefined") {
        Serial.print("json_failed\r\n");
        return;
    }
    handle(data["type"], data["device"], data["option"], data["num"]);
    /*
        data["t(ype)"]: svo/eng
        data["d(evice)"]: al, ar, tl, tr
        data["o(ption)"]: s(et)/q(uery)
        data["n(um)"]: SHORT
    */
}