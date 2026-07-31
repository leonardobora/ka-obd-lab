# ka-obd-lab

Parte 1 da série "projetos de garagem (de quarto)" — [parte 2 foi as luzes RGB](https://github.com/leonardobora/rgb-hub).

Projeto de leitura/telemetria do Ford Ka 2017 via OBD-II, com objetivo de
evoluir depois pra engenharia reversa do barramento CAN (ver histórico da
conversa pro plano completo de camadas: OBD genérico -> FORScan/módulos
Ford -> sniff bruto de CAN).

## Visão geral do plano

```mermaid
flowchart TD
    car["Ford Ka 2017"] -->|porta OBD-II| t1(("Tier 1<br/>OBD-II genérico"))
    t1 --> t2(("Tier 2<br/>FORScan / módulos Ford"))
    t2 --> t3(("Tier 3<br/>CAN bus bruto"))

    t1 -.-> t1d["RPM, velocidade, temperatura,<br/>DTCs, VIN — feito neste repo"]
    t2 -.-> t2d["BCM, IPC, config as-built<br/>(precisa adaptador MS/HS-CAN)"]
    t3 -.-> t3d["Sniff + engenharia reversa<br/>de sinais não documentados"]

    classDef done fill:#2ecc71,stroke:#27ae60,color:#fff
    classDef next fill:#f1c40f,stroke:#f39c12,color:#000
    classDef future fill:#95a5a6,stroke:#7f8c8d,color:#fff

    class t1 done
    class t2 next
    class t3 future
```

Este repo cobre o **Tier 1**. Os próximos dois ainda são plano, não código.

## Hardware

Scanner ELM327 WiFi/Bluetooth (Axscan, v2.1) — a caminho. Modo WiFi é o
recomendado pra automação (vira socket TCP simples, sem pareamento BT).

## Arquivos

- `pids.py` — definição dos PIDs OBD-II (modo 01) lidos hoje: rpm, speed,
  coolant_temp, throttle_position, intake_air_temp, engine_load, maf,
  fuel_level, battery_voltage. Fácil adicionar novos.
- `obd_client.py` — cliente ELM327 cru (sem lib python-obd), fala AT/OBD
  direto por WiFi (TCP) ou serial (COM port, quando pareado por Bluetooth/USB).
- `read_live.py` — script principal, lê PIDs em loop e imprime no terminal.
- `mock_elm327.py` — simula um ELM327 por TCP local, pra testar o client
  sem o scanner físico. Gera valores variando com o tempo (não fixos), pra
  validar de verdade o parsing.

## Arquitetura atual

```mermaid
flowchart LR
    subgraph fonte["Fonte de dados"]
        real["Scanner ELM327 real<br/>(WiFi)"]
        mock["mock_elm327.py<br/>(simulador TCP)"]
    end

    real -->|socket TCP| client["obd_client.py<br/>ELM327Client"]
    mock -->|socket TCP| client

    pids["pids.py<br/>definição dos PIDs"] --> client

    client --> reader["read_live.py<br/>loop de leitura"]
    reader --> terminal[["Terminal<br/>rpm / speed / temp / ..."]]
    reader -.->|planejado| csvlog[("Log CSV<br/>com timestamp")]
```

`read_live.py` não sabe (nem precisa saber) se está falando com o carro
de verdade ou com o mock — os dois falam o mesmo protocolo ELM327 na
mesma porta TCP. Foi assim que a leitura foi validada antes do scanner
chegar.

## Uso

Quando o scanner chegar (modo WiFi, IP padrão costuma ser `192.168.0.10:35000`,
conecta o PC na rede WiFi que o adaptador cria):

```
python read_live.py --wifi
```

Testar sem o scanner (contra o mock):

```
python mock_elm327.py --port 35010
# em outro terminal:
python read_live.py --wifi --host 127.0.0.1 --port 35010
```

Já validado localmente (init + decodificação de rpm/speed/coolant/throttle/
engine_load todos corretos contra o mock).

## Próximos passos possíveis

- Validar com o scanner real assim que chegar.
- Ler DTCs (modo 03) e VIN (modo 09).
- Logar leituras em CSV com timestamp (base pra qualquer análise depois).
- Decidir sobre Tier 2 (adaptador MS/HS-CAN + FORScan) e Tier 3 (CANable +
  fluxo próprio de engenharia reversa de CAN, inspirado no skill da
  CSS Electronics mas sem depender do hardware CANsub).
