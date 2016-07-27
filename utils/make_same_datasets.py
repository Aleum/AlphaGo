
if __name__ == "__main__":
    x = open(r'C:\Users\Aleum\Desktop\original_dataset\game_033.sgf_65_x.csv').read()
    y = open(r'C:\Users\Aleum\Desktop\original_dataset\game_033.sgf_65_y.csv').read()
    
    for i in range(0, 1000):
        open(r'C:\Users\Aleum\Desktop\same_dataset\\'+str(i)+"_x2.csv","w+").write(x)
        open(r'C:\Users\Aleum\Desktop\same_dataset\\'+str(i)+"_y2.csv","w+").write(y)

    print "finish"
        