#include <stdint.h>
#include <stdio.h>
#include "stm32f10x.h"
// "stm32f4xx.h" // Ou le fichier d'en-tête correspondant à votre microcontrôleur


#define ADXL345_POWER_CTL 0x2D // Adresse du registre DATA_FORMAT
#define ADXL345_DATA_FORMAT 0x31 // Adresse du registre DATA_FORMAT
#define ADXL345_BW_RATE  0x2C // Adresse du registre BW_RATE
#define ADXL345_FIFO_CTL 0x38 // Adresse du registre FIFO_CTL
#define ADXL345_INT_ENABLE  0x2E // Adresse du registre INT_ENABLE
#define ADXL345_INT_MAP     0x2F // Adresse du registre INT_MAP
#define ADXL345_DATAX0 0x32
#define ADXL345_DATAX1 0x33
#define ADXL345_DATAY0 0x34
#define ADXL345_DATAY1 0x35
#define ADXL345_DATAZ0 0x36
#define ADXL345_DATAZ1 0x37
#define ADXL345_DEVID 0x00 // Adresse du registre contenant l'ID (par défaut 0xE5)

// #define SPI_SR_TXE (1<<1)
// #define SPI_SR_RXNE (1<<0)

// Définitions
#define CS_PIN (1<<12)       // Broche CS connectée à PB12
#define CS_PORT GPIOB            // Port GPIO pour CS


// Temporisation simple
void DELAY(volatile unsigned int delay)
{
    volatile unsigned int i;
    for(i = 0; i < (delay * 5400); i++) ;
}


// Fonction d'initialisation GPIOA
void init_gpioA(unsigned char num_bit, unsigned int quartet_config) {
    // Calculez la position du quartet de bits à configurer dans CRL ou CRH
    unsigned char bit_ref = (num_bit * 4) & 31;

    // Activer l'horloge pour GPIOA : Bit 2 dans RCC->APB2ENR doit être mis à 1
    RCC->APB2ENR |= (1 << 2);

    // Limiter quartet_config à 4 bits
    quartet_config &= 0xF;

    // Configurer le registre CRL si le numéro de bit est inférieur à 8
    if (num_bit < 8) {
        // Effacer les anciens bits du quartet correspondant dans CRL
        GPIOA->CRL &= ~(0xF << bit_ref);
        // Configurer les nouveaux bits du quartet dans CRL
        GPIOA->CRL |= (quartet_config << bit_ref);
    } else {
        // Effacer les anciens bits du quartet correspondant dans CRH
        GPIOA->CRH &= ~(0xF << bit_ref);
        // Configurer les nouveaux bits du quartet dans CRH
        GPIOA->CRH |= (quartet_config << bit_ref);
    }
}


// Initialisation des GPIO pour les broches SPI2
void init_gpioB(unsigned char num_bit, unsigned int quartet_config) {
    unsigned char bit_ref = (num_bit * 4) & 31;

    // Activer l'horloge pour GPIOB : RCC->APB2ENR bit 3
    RCC->APB2ENR |= (1 << 3);

    // Limiter quartet_config   4 bits
    quartet_config &= 0xF;

    if (num_bit < 8) {
        GPIOB->CRL &= ~(0xF << bit_ref);  // Effacer les anciens bits dans CRL
        GPIOB->CRL |= (quartet_config << bit_ref);  // Configurer les nouveaux bits
    } else {
        GPIOB->CRH &= ~(0xF << bit_ref);  // Effacer les anciens bits dans CRH
        GPIOB->CRH |= (quartet_config << bit_ref);  // Configurer les nouveaux bits
    }
}

// Initialisation du SPI2 (maître)
void init_SPI2(void) {
    // Activer les horloges AFIO et SPI2
    RCC->APB2ENR |= (1 << 0);  // Horloge AFIO
    RCC->APB1ENR |= (1 << 14);  // Horloge SPI2

    // Configuration des broches SPI (PA4=SS, PA5=SCLK, PA6=MISO, PA7=MOSI)
    init_gpioB(12, 0x3);  // PB12 (SS) : Output push-pull, max speed 50 MHz
    init_gpioB(13, 0xB);  // PB13 (SCLK) : Alternate function output push-pull
    init_gpioB(14, 0x8);  // PB14 (MISO) : Input avec pull-up
    GPIOB->ODR |= (1 << 14);  // Activer la pull-up sur PB14 (MISO)
    init_gpioB(15, 0xB);  // PB15 (MOSI) : Alternate function output push-pull

    // Configurer SPI1 en mode maître
    SPI2->CR1 = 0;  // Réinitialisation
    SPI2->CR1 |= (1 << 2);  // Sélection du maître (MSTR = 1)
    
    // Configurer la fréquence d'horloge SPI : fpclk / 32 (BR = "100")
    SPI2->CR1 |= (7 << 3);  // BR[2:0] = 100, diviseur d'horloge par 32
    
    // CPOL = 0, CPHA = 0 : Front montant pour l'échantillonnage des données
    SPI2->CR1 |= (1 << 0); // CPHA=0
    SPI2->CR1 |= (1 << 1);  // CPOL=1
    
    // DFF = 0 : Communication en 8 bits
    SPI2->CR1 &= ~(1 << 11);  // DFF=0 pour 8 bits

    // Activer SS output enable (SSOE) dans CR2 pour contrôler SS automatiquement
    SPI2->CR2 |= (1 << 2);

    // Activer SPI (SPE)
    SPI2->CR1 |= (1 << 6);  // SPE = 1
}


// Fonction d'initialisation de l'USART2
void init_USART2(void)
{
    /* Activer l'horloge pour l'USART2 */
    // Complétez cette ligne pour activer l'horloge USART2 (Bit ?? dans RCC->APB1ENR)

    RCC->APB1ENR |= (1<<17)    /* À compléter */;

    /* Configurer les broches PA2 (TX) et PA3 (RX) */
    // PA2 (TX) doit être configurée en mode alternate function output push-pull
    // Complétez la fonction init_gpioA pour configurer PA2 avec la bonne valeur de quartet_config
    /* À compléter : valeur correcte pour TX (alternate function output push-pull) */
    init_gpioA(2, 9);

    // PA3 (RX) doit être configurée en mode floating input
    // Complétez la fonction init_gpioA pour configurer PA3 avec la bonne valeur de quartet_config
    /* À compléter : valeur correcte pour RX (input floating) */
    init_gpioA(3, 4);

    /* Configurer le baudrate à 9600 bps */
    
	// Le baudrate est calculé avec Fpclk / Baudrate
    // Fpclk pour USART2 est sur APB1, donc 36 MHz, et le baudrate est 9600
    USART2->BRR = 36000000/9600;/* À compléter : valeur correcte du baudrate avec Fpclk = 36 MHz */

    /* Configurer l'USART2 pour 8 bits de données, 1 bit de stop */
    // Bit 13 dans CR1 doit être mis à 1 pour activer l'USART
    // Bit 12 dans CR1 doit être mis à 0 pour sélectionner une taille de mot de 8 bits
    // Bit 2 et Bit 3 dans CR1 doivent être activés pour la transmission et la réception
    USART2->CR1 = (1<<13) | (3<<2);/* À compléter : activer USART, transmission et réception */
    //0x200

    /* Configurer 1 bit de stop */
    // Bits 13:12 dans CR2 doivent être mis à 00 pour configurer 1 bit de stop
    USART2->CR2 &= ~(3<<12);
}

void send_USART2(char data) {
	// Attendre que le registre DR soit prêt à recevoir une nouvelle donnée (Bit 7 de SR = 1)
        while (!(USART2->SR  & (1<<7)));
        // Transmettre 
        USART2->DR = data;
}

void send_string(char* s) {
	int i = 0;
	while(s[i]) {
		send_USART2(s[i]);
		i++;
	}
}



uint8_t spi2_send_receive_byte_sans_CS(uint8_t data) {
    uint8_t retour;

    // 1. Attendre que le tampon de transmission (TXE) soit prêt
    while (!(SPI2->SR & SPI_SR_TXE)) {
        // Attente active jusqu'à ce que TXE soit à 1
    }

    // 2. Envoyer l'octet
    SPI2->DR = data;

    // 3. Attendre que la réception soit complète (RXNE)
    while (!(SPI2->SR & SPI_SR_RXNE)) {
        // Attente active jusqu'à ce que RXNE soit à 1
    }

    // 4. Lire et renvoyer l'octet reçu
    retour = SPI2->DR;

    return retour;
}



//fait 
//CS + Data + CS
uint8_t config_regADXL(uint8_t reg, uint8_t data) { 
	uint8_t reponse;
	//activer   le CS de l adxl
	CS_PORT -> ODR &= ~CS_PIN;

	//envoyer l adresse en positionnant bien le bit demande d ecriture pour l adxl
	spi2_send_receive_byte_sans_CS(reg); // S'assurer que le MSB est 0 (mode écriture)

	//envoyer la data 
	reponse = spi2_send_receive_byte_sans_CS(data);

	//desactiver   le CS de l adxl
	
	CS_PORT -> ODR |= CS_PIN;
	
	return reponse;
 }


	
void init_adxl_345(void){

    //initialiser power : sequence en plusieurs étapes conseillée
    config_regADXL(ADXL345_POWER_CTL, (ADXL345_POWER_CTL) & (0xFC));// Wakeup          fait D0 ET D1 à 0  = 8hz
    config_regADXL(ADXL345_POWER_CTL, (ADXL345_POWER_CTL) | (0x08) );// Measure         fait
 //**************DATA FORMAT ***********************   
    // FORMAT DES DONNES  :  passer en 16G justifié droit 
    // B7 : self test : garder à 0
    // B6 : mode SPI 3 ou SPI 4 fils : mettre 0 pour selectionner le mode 4 FILS
    // B5 : niveau logique des ITs   : mettre 1 = /int         mettre 0   =  int (actif haut) : mettre 1
    // B4 : laisser à 0
    // B3 : Full_ RES : mettre 1 pour disposer de plus de bits possibles
    // B2 : JUSTIFICATION DES DATAs  :  1 left justify, 0 right justify avec extension de signe : mettre 0 
    // B1 B0 : sensibilité : mettre 00 pour 2G , 01 pour 4G, 10 pour 8G, 11 pour 16G :   11
    // choix  choisir /IT et Full resolution et 16G   
    config_regADXL(ADXL345_DATA_FORMAT, 0x23);        // 0b00101111 = 0x2F
 
 //**************inactivité/ choc niveau 1*********************
    //D7 : activité DC ou AC   (absolu ou relatif aux précédentes mesures) :mettre 1 pour choisir AC
    //D6 : activité sur X
    //D5 : activité sur Y 
    //D4 : activité sur Z  
    //D3 : inactivité DC ou AC   (absolu ou relatif aux précédentes mesures) :mettre 1 pour choisir AC
    //D2 : inactivité sur X
    //D1 : inactivité sur Y 
    //D0 : inactivité sur Z  
    // on va dire qu'il y a activité si on détecte une activité sur X Y ou Z
    // on va dire qu'il y a inactivité si on ne détecte rien ni sur X ni sur Y ni sur Z en mode AC
  //  config_regADXL(ADXL345_ACT_INACT_CTL, 0xFF);
    
    // la valeur est par pas de 62.5mG  ainsi  256 correspondrait à 16G : mettre 
  //  config_regADXL(ADXL345_THRESH_ACT,16 );
  //  config_regADXL(ADXL345_THRESH_INACT,8 );
  //  config_regADXL(ADXL345_TIME_INACT, 1 );//sec 1-255
    
 //**************choc*******************   
    //D7 à D4 non definis : 0
    //D3 : suppress double tap si acceleration reste elevée entre les TAP avec valeur 1
    //D2 : tap X enable si 1
    //D1 : tap Y enable si 1
    //D0 : tap Z enable si 1
    
  // config_regADXL(ADXL345_TAP_AXES, 0x0F); // detection choc de tous les cotés
  // config_regADXL(ADXL345_THRESH_TAP, 0xA0); // detection choc réglée à 10G
  // config_regADXL(ADXL345_DUR, 16); // duree minimale du choc 625us increment ici 10ms
 //  config_regADXL(ADXL345_LATENT, 0x00); // ecart minimum entre tap pas 1.25ms : 0 desactive
 //  config_regADXL(ADXL345_TAP_AXES, 0x00); // fenetre seconde frappe pas 1.25ms : 0 desactive
 
 //***************************************
   
  // config_regADXL(ADXL345_THRESH_FF, ); // seuil detection FREE FALL  pas 62.5mG 0.6G
  // config_regADXL(ADXL345_TIME_FF,); // duree minimale de chute pas 5ms  : 100 ms =20
  
 //*************************************
 //interruptions  activer les ITs : ADXL345_INT_ENABLE  bit à 0 = INT1 , bit à 1 = INT2
 // selectionner patte INT1 ou INT2: ADXL345_INT_MAP
 // en cas de selection multiple, la lecture de ADXL345_INT_SOURCE
   // pour les deux registres, meme emplacement :
   // B7 = DATA_READY
   // B6 = SINGLE_TAP
   // B5 = DOUBLE_TAP
   // B4 = ACTIVITY
   // B3 = INACTIVITY
   // B2 = FREE_FALL
   // B1 = WATER_MARK  (niveau remplissage FIFO)
   // B0 = OVERRUN     (pas lu assez frequemment)
    //config_regADXL(ADXL345_INT_ENABLE, 0x00);
    //config_regADXL(ADXL345_INT_MAP, ); // tout le monde en INT 2 sauf DATA_READY
    //config_regADXL(ADXL345_INT_ENABLE, ); // Juste data rdy


    // Désactiver toutes les interruptions initialement
    config_regADXL(ADXL345_INT_ENABLE, 0x00);

    // Mapper DATA_READY sur INT1, et toutes les autres interruptions sur INT2
    config_regADXL(ADXL345_INT_MAP, 0x7F);

    // Activer uniquement l'interruption DATA_READY
    config_regADXL(ADXL345_INT_ENABLE, 0x80);
	
  //*************************************
  //gestion par FIFO pour stocker sans danger  
   //ADXL345_FIFO_CTL : les 4 bits de poids faible choisissent le débit (voir doc))
    //F : 3200Hz, E:1600, D:800, C:400, B:200, A:100, 9:50, 8:25, 7:12.5, 6:6.25, 5:3.125, 
   // ADXL345_FIFO_CTL : 
    // bits B7 B6   : 
    // 00 bypass (no fifo)
    // 01 FIFO (blocage plein) 
    // 10 STREAM (ecrasement) 
    // 11 Trigger (photo evenement)
    // bit B5  Trigger sur INT1 (0) ou INT2 (1)
    // bit B4 à B0 : niveau remplissage pour watermark
    
    config_regADXL(ADXL345_BW_RATE, 0x0A );  // Fonctionnement à 100 HZ
    config_regADXL(ADXL345_FIFO_CTL, 0xA0); // stream, trig int1, avertissement sur mi remplissage (16)

}


//inutile ici
/*
void spi2_send_byte_sans_CS(uint8_t data)
{   unsigned char poubelle;
    // 1. Attendre que le registre de données soit vide (TXE de SR)
    while (!(SPI2->SR & SPI_SR_TXE))
    {
        // Attente active
    }

// 2. Envoyer l'octet  data 
    SPI2->DR = data;  

	 // 3. Attendre que la réception soit complète (RXNE) 
	// car cela indique qu on a fini l envoi aussi*
    while (!(SPI2->SR & SPI_SR_RXNE))
    {
        // Attente active
    }

    // 4. Lire l'octet reçu pour purger le SPI IN (le mettre dans la poubelle
    poubelle = SPI2->DR;
    // Le tampon de réception est maintenant purgé

}
*/




	void read_ADXL_sensors( void)
{		
		char buffer[80];
    uint8_t x0, x1, y0, y1, z0, z1; // Variables pour stocker chaque octet
    int16_t x, y, z;               // Variables pour les valeurs complètes de chaque axe
	float xf, yf, zf;

    //activer   le CS de l adxl
    //digitalWrite(CS_PIN, LOW);

    //declencher une lecture multiple à l adresse du registre ADXL345_DATAX0 (attention aux bits B7 et B6)
    x0 = config_regADXL(ADXL345_DATAX0 | 0x80, 0xFF); // Lecture de DATA_X0 lecture mutiple 
    x1 = config_regADXL(ADXL345_DATAX1 | 0x80, 0xFF); // Lecture de DATA_X1 lecture mutiple 
    y0 = config_regADXL(ADXL345_DATAY0 | 0x80, 0xFF); // Lecture de DATA_Y0 lecture mutiple  
    y1 = config_regADXL(ADXL345_DATAY1 | 0x80, 0xFF); // Lecture de DATA_Y1 lecture mutiple  
    z0 = config_regADXL(ADXL345_DATAZ0 | 0x80, 0xFF); // Lecture de DATA_Z0  lecture mutiple  
    z1 = config_regADXL(ADXL345_DATAZ1 | 0x80, 0xFF); // Lecture de DATA_Z1 lecture mutiple  



    // Combiner les octets pour chaque axe (MSB et LSB)
    x = (int16_t)((x1 << 8) | (x0>>0));
	if(x&(1<<9)) x |= (0xff<<10);
    y = (int16_t)((y1 << 8) | (y0>>0));
		if(y&(1<<9)) y |= (0xff<<10);
    z = (int16_t)((z1 << 8) | (z0>>0));
		if(z&(1<<9)) z |= (0xff<<10);
		
		xf = 32. / 1024. *(float)x ;
		yf = 32. / 1024. *(float)y ;
		zf = 32. / 1024. *(float)z ;


    sprintf(buffer, "x: %4X \t %i \t %.3f\n\ry: %4X \t %i \t %.3f\n\rz: %4X \t %i \t %.3f\n\r\n\r", x, x, xf, y, y, yf, z, z, zf);
		send_string(buffer);


    
   //desactiver   le CS de l adxl
    // digitalWrite(CS_PIN, HIGH);
}		




void return_ID(void) {
    uint8_t ID;
	char buffer[20];

    ID = config_regADXL(ADXL345_DEVID | 0x80, 0xFF);

    // Afficher l'ID sur le moniteur série
    sprintf(buffer, "ID: %2X\n\r", ID);
		send_string(buffer);
}




int main(void) {
    // Initialisation des périphériques
    init_USART2();        // Initialiser la communication série

    // Configurer le SPI
		init_SPI2();

    // Initialisation de l'ADXL345
    init_adxl_345();

    while (1) {
        // Lire et afficher l'ID du capteur
        //return_ID();

        // Attendre 1 seconde avant de relire
        //DELAY(1000);
			
			// lire les capteurs
			read_ADXL_sensors();
			
			DELAY(1000);
    }

}