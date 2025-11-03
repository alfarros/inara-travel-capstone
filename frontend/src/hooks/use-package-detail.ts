
// src/hooks/use-package-detail.ts
import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Package } from "@/data/packages"; // Import interface Package
import { packagesData } from "@/data/packages";

export const usePackageDetail = () => {
  const { id } = useParams<{ id: string }>();
  const [packageDetail, setPackageDetail] = useState<Package | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPackage = () => {
      setIsLoading(true);
      const foundPackage = packagesData.find((pkg) => pkg.id === Number(id)); // Ubah id menjadi Number
      setPackageDetail(foundPackage || null);
      setIsLoading(false);
    };

    if (id) {
      fetchPackage();
    }
  }, [id]);

  return { packageDetail, isLoading };
};