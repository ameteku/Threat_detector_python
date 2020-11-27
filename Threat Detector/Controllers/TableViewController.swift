//
//  TableViewController.swift
//  Threat Detector
//
//  Created by Ebo Sompa Dennis on 11/14/20.
//  Copyright © 2020 Ebo Sompa Dennis. All rights reserved.


import Firebase

import UIKit

class TableViewController: UITableViewController {
    
    var ref: DatabaseReference! = Database.database().reference()
    
    var events: [Event] = []
    
    @IBOutlet var myTableView: UITableView!
    
    @IBAction func refreshPressed(_ sender: UIButton) {
        events.removeAll()
        loadMessages()
    }
    

    override func viewDidLoad() {
        super.viewDidLoad()
        loadMessages()
        print(events)
        
        myTableView.dataSource = self

        // Uncomment the following line to preserve selection between presentations
        // self.clearsSelectionOnViewWillAppear = false

        // Uncomment the following line to display an Edit button in the navigation bar for this view controller.
        // self.navigationItem.rightBarButtonItem = self.editButtonItem
    }
    
    func getData(from url: URL, completion: @escaping (Data?, URLResponse?, Error?) -> ()) {
        URLSession.shared.dataTask(with: url, completionHandler: completion).resume()
    }
    /*
    
    func downloadImage(from url: URL) {
        print("Download Started")
        getData(from: url) { data, response, error in
            guard let data = data, error == nil else { return }
            print(response?.suggestedFilename ?? url.lastPathComponent)
            print("Download Finished")
            DispatchQueue.main.async() { [weak self] in
                self?.imageView.image = UIImage(data: data)
            }
        }
    }
    */
    func loadMessages(){
        
        ref.child(K.FStore.structureName).child(K.FStore.collectionName).observeSingleEvent(of: .value, with: { (snapshot) in
          // Get user value
           
            let data = snapshot.value as! NSDictionary
//            data.sorted { (<#(key: Any, value: Any)#>, <#(key: Any, value: Any)#>) -> Bool in
//                <#code#>
//            }
            print(data)
            for (key,_) in data {
                let nne = data.value(forKey: key as! String) as! NSDictionary
                
                
                var messageF:String = nne.value(forKey: K.FStore.messageField) as? String ?? "None"
                messageF = messageF + " spotted"
                var timeF:String = nne.value(forKey: K.FStore.timeField) as? String ?? "Time"
                timeF = "at time " + timeF
                //var linkImage:String = nne.value(forKey:"link") as? String ?? "None"
                //let url = URL(string: linkImage)!
                let event = Event(message: messageF, time: timeF)
                
                
                //self.downloadImage(from: url)
                
                
                print(event)
                self.events.append(event)
                

            }
            self.myTableView.reloadData()


          // ...
          }) { (error) in
            print(error.localizedDescription)
        }
        
    }

    // MARK: - Table view data source
    /*
    override func numberOfSections(in tableView: UITableView) -> Int {
        // #warning Incomplete implementation, return the number of sections
        return 1
    }
     */
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // #warning Incomplete implementation, return the number of rows
        return events.count
    }

    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: K.cellIdentifier, for: indexPath)
        cell.textLabel?.text = events[indexPath.row].message
        print(events[indexPath.row].message)
        cell.detailTextLabel?.text = events[indexPath.row].time
        

        // Configure the cell...

        return cell
    }
    

    /*
    // Override to support conditional editing of the table view.
    override func tableView(_ tableView: UITableView, canEditRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the specified item to be editable.
        return true
    }
     
    */
    
    override func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        /*if let filePath = Bundle.main.path(forResource: "imageName", ofType: "jpg"), let image = UIImage(contentsOfFile: filePath) {
            imageView.contentMode = .scaleAspectFit
            imageView.image = image
        }*/
        
        //let mylink = events[indexPath.row].link
        
        /*
        if let email = emailTextfield.text, let password = passwordTextfield.text {
                    Auth.auth().signIn(withEmail: email, password: password) { authResult, error in
                        if let e = error{
                            print(e.localizedDescription)
                        } else {
                            self.performSegue(withIdentifier: K.loginSegue, sender: self)
                        }
                    }
                }
    */
    }

    /*
    // Override to support editing the table view.
    override func tableView(_ tableView: UITableView, commit editingStyle: UITableViewCell.EditingStyle, forRowAt indexPath: IndexPath) {
        if editingStyle == .delete {
            // Delete the row from the data source
            tableView.deleteRows(at: [indexPath], with: .fade)
        } else if editingStyle == .insert {
            // Create a new instance of the appropriate class, insert it into the array, and add a new row to the table view
        }    
    }
    */

    /*
    // Override to support rearranging the table view.
    override func tableView(_ tableView: UITableView, moveRowAt fromIndexPath: IndexPath, to: IndexPath) {

    }
    */

    /*
    // Override to support conditional rearranging of the table view.
    override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
        // Return false if you do not want the item to be re-orderable.
        return true
    }
    */

    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
