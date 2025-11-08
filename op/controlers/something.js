// Tutorial del cliente de Open Payments
// Objetivo: Realizar un pago entre pares entre dos direcciones de billetera (usando cuentas en la cuenta de prueba)

// https://ilp.interledger-test.dev/client-sdbk24

// https://ilp.interledger-test.dev/receiver-sbdk24

// https://ilp.interledger-test.dev/receptor-sdbk24


// ConfiguraciÃ³n inicial

import { createAuthenticatedClient, isFinalizedGrant } from "@interledger/open-payments";

import fs from "fs";
import { createInterface } from "readline";
//import { send } from "process";
import Readline from  "readline/promises";

// a. Importar dependencias y configurar el cliente

(async () => {
    const privateKey = fs.readFileSync("private.key", "utf8");
    const client = await createAuthenticatedClient({
        walletAddressUrl: "https://ilp.interledger-test.dev/paguito-sender",
        privateKey, // puedes usar la forma corta
        keyId: "f5a43f8c-bfff-4daf-81e8-798db41e4518", 
    });

    // b. Crear una instancia del cliente Open Payments
    // c. Cargar la clave privada del archivo
    // d. Configurar las direcciones de las billeteras del remitente y el receptor

    // Flujo de pago entre pares
    // 1. Obtener una concesiÃ³n para un pago entrante)

    const sendingWalletAddress = await client.walletAddress.get({
        url: "https://ilp.interledger-test.dev/paguito-sender"
    });

    const receiveWalletAddress = await client.walletAddress.get({
        url: "https://ilp.interledger-test.dev/receptor-sdbk24"
    });

    console.log(sendingWalletAddress, receiveWalletAddress);
    // 2. Obtener una concesiÃ³n para un pago entrante
    const incomingPaymentGrant = await client.grant.request(
        {
            url: receiveWalletAddress.authServer,
        },
        {
            access_token: {
                access: [
                    {
                        type: "incoming-payment",
                        actions: ["create"],
                    }
                ]
            }
        }
    );


    if (!isFinalizedGrant(incomingPaymentGrant)) {
        throw new Error("Se espera finalice la concesion");
    }

    console.log(incomingPaymentGrant);
    // 3. Crear un pago entrante para el receptor
    const incomingPayment = await client.incomingPayment.create({
        url: receiveWalletAddress.resourceServer,
        accessToken: incomingPaymentGrant.access_token.value,
    },
    {
        walletAddress: receiveWalletAddress.id,
        incomingAmount: {
            assetCode: receiveWalletAddress.assetCode,
            assetScale: receiveWalletAddress.assetScale,
            value: "10000",
        },
    }

);

console.log({ incomingPayment  });
    // 4. Crear un concesiÃ³n para una cotizaciÃ³n
const quoteGrant = await client.grant.request(
    {
        url: sendingWalletAddress.authServer,
    },
    {
        access_token: {
            access: [
                {
                    type: "quote",
                    actions: [ "create" ],
                }
            ]
        }
    }
);

if (!isFinalizedGrant(quoteGrant)) {
    throw new Error("Se espera finalice la concesion")
}

console.log(quoteGrant);
    // 5. Obtener una cotizaciÃ³n para el remitente
const quote = await client.quote.create(
    {
        url: receiveWalletAddress.resourceServer,
        accessToken: quoteGrant.access_token.value,
    },
    {
        walletAddress: sendingWalletAddress.id,
        receiver: incomingPayment.id,
        method: "ilp",
    }
);

console.log({ quote });

    // 6. Obtener una concesiÃ³n para un pago saliente

const outgoingPaymentGrant = await client.grant.request(
    {
        url: sendingWalletAddress.authServer,
    },
    {
        access_token: {
            access: [
                {
                    type: "outgoing-payment",
                    actions: [ "create" ],
                    limits: {
                        debitAmount: quote.debitAmount,
                    },
                    identifier: sendingWalletAddress.id,
                }
            ]
        },
        interact: {
            start: [ "redirect" ],
        },
    }
);

console.log({ outgoingPaymentGrant });
    // 7. Continuar con la concesiÃ³n del pago saliente
await Readline
    .createInterface({
        input: process.stdin,
        output: process.stdout,
    })
    .question("Presiona para continuar con el pago saliente...");
    // 8. Finalizar la concesiÃ³n del pago saliente
const finalizedOutgoingPaymentGrant = await client.grant.continue({
        url: outgoingPaymentGrant.continue.uri,
        accessToken: outgoingPaymentGrant.continue.access_token.value,
    });
    if (!isFinalizedGrant(finalizedOutgoingPaymentGrant)) {
        throw new Error("Se espera finalice la consesión");
    }
    // 9. Continuar con la cotizaciÃ³n de pago saliente
const outgoingPayment = await client.outgoingPayment.create(
    {
        url: sendingWalletAddress.resourceServer,
        accessToken: finalizedOutgoingPaymentGrant.access_token.value,
    },
    {
        walletAddress: sendingWalletAddress.id,
        quoteId: quote.id,
    }
);

console.log({ outgoingPayment });

})(); 