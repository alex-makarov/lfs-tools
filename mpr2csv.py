import pyinsim9
import datetime

class PlayerInfo:
    name = "Unknown"
    position = 0
    lap = 0
    lap_start_time = 0
    s1 = -1
    s2 = -1
    s3 = -1

class TrackInfo:
    s1_node = -1
    s2_node = -1
    s3_node = -1
    num_nodes = 0

# Globals
Players = dict()
Track = TrackInfo()
Time = 0

# Init CSV file with current time in filename
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
file = open(f"laps-{timestamp}.csv", "w")
file.write("Player, Lap, Position, Time, S1, S2, S3, TotalTime\n")


def init(insim):
    print ('InSim initialized')
    

def closed(insim):
    print ('InSim connection closed. Have you enabled insim with /insim=29999 in LFS?')
    

def error(insim):
    print ('InSim error:')
    import traceback
    traceback.print_exc()


def lap_completed(insim, lap):
    global Players, Time
    p = Players[lap.PLID]
    p.lap = lap.LapsDone

    print (f"{p.name} lap {lap.LapsDone} t={lap.LTime/1000.0}s, p {Players[lap.PLID].position}")
    file.write(f"\"{p.name}\", {lap.LapsDone}, {p.position}, {lap.LTime/1000.0}, {p.s1/100.0}, {p.s2/100.0}, {p.s3/100.0}, {lap.ETime/1000.0}\n")
    file.flush()

    p.lap_start_time = Time
    p.s1 = -1
    p.s2 = -1
    p.s3 = -1


def player_tracking(insim, nlp:pyinsim9.IS_NLP):
    global Track, Players, Time
    for i in range (0,nlp.NumP):
        info = nlp.Info[i]
        id = info.PLID

        if not id in Players:
            Players[id] = PlayerInfo()

        p = Players[id]
        p.position = info.Position
        p.lap = info.Lap

        match int(info.Node):
            case Track.s1_node:
                if p.s1 == -1:
                    p.s1 = Time - p.lap_start_time
                    print(f"{p.name} S1 = {p.s1/100.0}s")
            case Track.s2_node:
                if p.s2 == -1:
                    p.s2 = Time - p.lap_start_time
                    print(f"{p.name} S2 = {p.s2/100.0}s")
            case Track.s3_node:
                if p.s3 == -1:
                    p.s3 = Time - p.lap_start_time
                    print(f"{p.name} S3 = {p.s3/100.0}s")

    insim.send(pyinsim9.ISP_TINY, ReqI=255, SubT=pyinsim9.TINY_GTH)


def race_started (insim, rst:pyinsim9.IS_RST):
    global Track
    Track.s1_node = rst.Split1
    Track.s2_node = rst.Split2
    Track.s3_node = rst.Split3
    Track.num_nodes = rst.NumNodes
    print (f"Track info: Sectors: {Track.s1_node}, {Track.s2_node}, {Track.s3_node}, Nodes: {Track.num_nodes}")

    for player in Players.values():
        player.lap = 0
        player.lap_start_time = Time
        player.s1 = -1
        player.s2 = -1
        player.s3 = -1

    insim.send(pyinsim9.ISP_TINY, ReqI=255, SubT=pyinsim9.TINY_NPL)


def player_info (insim, npl:pyinsim9.IS_NPL):
        id = npl.PLID
        if not id in Players:
            Players[id] = PlayerInfo()

        Players[id].name = npl.PName.decode("utf-8")
        print (f"Player {id} is {Players[id].name}")


def small_message(insim, msg:pyinsim9.IS_SMALL):
    global Time
    if msg.SubT == pyinsim9.SMALL_RTP:
        Time = msg.UVal


def main():
    insim = pyinsim9.insim('127.0.0.1', 29999, Admin=b'YOUR-PASSWORD', UDPPort=3187, Interval=50, Flags=pyinsim9.ISF_NLP)

    insim.bind(pyinsim9.EVT_INIT, init)
    insim.bind(pyinsim9.EVT_CLOSE, closed)
    insim.bind(pyinsim9.EVT_ERROR, error)
    insim.bind(pyinsim9.ISP_LAP, lap_completed)
    insim.bind(pyinsim9.ISP_NLP, player_tracking)
    insim.bind(pyinsim9.ISP_RST, race_started)
    # This is for time tracking
    insim.bind(pyinsim9.ISP_SMALL, small_message)
    insim.bind(pyinsim9.ISP_NPL, player_info)

    # Request players info
    insim.send(pyinsim9.ISP_TINY, ReqI=255, SubT=pyinsim9.TINY_NPL)

    pyinsim9.run()

if __name__ == "__main__":
    main()
