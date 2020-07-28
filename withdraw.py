import time
import read_file


def withdraw(ls):
    

    current_balance = int(ls[3])
    
    print('Your current balance: ' + ls[3])

    withdraw_amount = int(input('Enter withdraw amount: '))

    if withdraw_amount > current_balance:
        print("ERROR: You can't withdraw more than your current balance")
    else:
        current_balance -= abs(withdraw_amount) 

    file_name = ls[0] + '.txt'
    process_list = read_file.read_file(file_name)
    id_file = open(file_name, 'a')

    if len(process_list) == 0:
        
        last_id = 1
    else:
        last_id = int(process_list[len(process_list)-1][0]) + 1
        

    id_file.write('{0}\twithdraw\t\t\t{1}\t{2}\t{3}\n'.format(str(last_id), str(time.ctime()), ls[3], str(current_balance)))
    
    id_file.close()
    ls[3] = str(current_balance)
    print('Your current balance: ' + ls[3])

    return ls
