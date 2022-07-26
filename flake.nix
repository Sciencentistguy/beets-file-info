{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      packages.beets-file-info = pkgs.python3Packages.buildPythonPackage {
        name = "beets-file-info";
        src = pkgs.lib.cleanSource ./.;
        nativeBuildInputs = with pkgs; [beets];
      };
      packages.default = self.packages.${system}.beets-file-info;
    });
}
