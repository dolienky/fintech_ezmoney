const P2PLending = artifacts.require("P2PLending");

module.exports = function(deployer) {
  deployer.deploy(P2PLending);
};
